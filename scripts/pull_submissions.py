import sys, json, re

from pathlib import Path
from praw import Reddit
from praw.models import Subreddit, Submission
from typing import Iterator, List
from functools import reduce

from tools import reddit
from tools import extract

basedir: Path = Path(__file__).parent
connection: Reddit = reddit.connect()
nearprog: Subreddit = connection.subreddit("nearprog")

new_way: bool = False

# core info from Submission
class Post:
    def __init__(self, submission: Submission) -> None:
        self.title: str = getattr(submission, "title")
        self.created_utc: float = getattr(submission, "created_utc")
        self.link_flair_text: str = getattr(submission, "link_flair_text")
        self.score: int = getattr(submission, "score")
        self.upvote_ratio: float = getattr(submission, "upvote_ratio")
        self.author: str = getattr(submission, "author")

    def is_song(self) -> bool:
        return ((self.link_flair_text != 'Discussion') and
                (self.link_flair_text != 'Contest') and
                (self.link_flair_text != 'Announcement') and
                ('[Discussion]' not in self.title))

    def as_raw(self) -> str:
        keys = ["title", "created_utc", "link_flair_text", "score", "upvote_ratio", "author"]
        values = map(lambda k: str(getattr(self, k)), keys)
        return reduce((lambda a, b: f"{a};;{b}"), values)

def fetch_posts(limit: int = None) -> Iterator[Post]:
    submissions = nearprog.top("all", limit=limit)
    posts = map(lambda s: Post(s), submissions)
    return filter(lambda post: post.is_song(), posts)

# fetch and parse post data
def posts(limit = None, fetch = True, parse = True, export = False):
    typed_fields = [("str",   "title"),
                    ("float", "created_utc"),
                    ("str",   "link_flair_text"),
                    ("int",   "score"),
                    ("float", "upvote_ratio"),
                    ("str",   "author")]

    types, fields = zip(*typed_fields)

    out_raw    = "data/posts_raw.txt"
    out_parsed = "data/posts_parsed.json"

    # (1) fetch new data from Reddit, optionally save to raw output file
    if (fetch):

        if (new_way):
            fetched_posts = list(map(lambda p: p.as_raw(), fetch_posts(limit)))

        else:
            def get_fields(submission):
                return list(map(lambda x: str(getattr(submission, x)), fields))
                
            # fetch post fields and separate with double semicolons (;;)
            all_posts = nearprog.top("all", limit=limit)
            song_posts = filter(lambda submission: reddit.is_song(submission), all_posts)
            fetched_posts = [";;".join(get_fields(post)) for post in song_posts]

        # export to output file as optional side effect
        if (export):
            with (basedir / out_raw).open('w') as outfile:
                for row in fetched_posts:
                    print(row, file=outfile)

        # if we're fetching but not exporting, print to terminal (testing)
        else:
            for row in fetched_posts:
                print(row)
            print("")

    # (2) parse submissions from memory or from raw file as input file
    if (parse):
        max_field_width = max(len(max(fields, key=len)), len("raw_title")) + 2

        if (export):
            infile = (basedir / out_raw).open('r')
            outfile = (basedir / out_parsed).open('w')
        else:
            infile = fetched_posts
            outfile = sys.stdout

        # with fi as infile, fo as outfile:

        # open the JSON object for the first post
        print('[{', file=outfile)

        # write a "}, {" before every entry except the first
        first_row = True

        for row in infile:
            if (first_row == False):
                print("}, {", file=outfile)
            first_row = False

            # split the input into field values
            field_values = row.split(";;")

            # write the non-title fields (we'll parse "title" below)
            for field in fields:
                if (field != "title"):
                    field_type  =        types[fields.index(field)]
                    field_value = field_values[fields.index(field)]
                    if (field_type == "str"):
                        field_value = '"' + field_value.strip() + '"'
                    else:
                        field_value = eval(f'{field_type}(field_value)')
                    field += '"'
                    print(f'  "{field:{max_field_width}s}: {field_value},', file=outfile)

            # if raw.txt file contains a "title" field, try to parse it
            if ("title" in fields):
                raw_title = field_values[fields.index("title")].strip()
                artist, song = reddit.split_title(raw_title)

                # extract the [subgenre] tag, if there is one
                subgenre = ""
                subgenre_match = re.search(r'\[.+\]', song)
                if (subgenre_match != None):
                    (start, _) = subgenre_match.span()

                    # song[end:] contains commentary after the [subgenre] -- remove
                    song = (song[:start]).strip()
                    subgenre = re.sub(r'[\[\]]', '', subgenre_match.group())

                # extract "junk" parentheticals like (live), (1998), etc.
                (song, _) = extract.misc_parentheticals(song)

                # remove "" from around song title, if present
                if (song[0] == '"' and song[-1] == '"'):
                    song = song[1:-1]

                # if no existing subgenre, try to extract (subgenre) in () instead of in []
                if (subgenre == ""):
                    (new_song, subgenre) = extract.parenthetical_subgenre(song)

                    # we inferred a subgenre
                    if (subgenre != ""):
                        song = new_song
                        subgenre = subgenre

                # try to extract multiple artists separated by "," and "and"
                artists = json.dumps(extract.multiple_artists(artist))

                addl_fields = ["raw_title\"", "artists\"", "song\"", "subgenre\""]
                addl_values = [json.dumps(raw_title.strip()), artists, json.dumps(song), json.dumps(subgenre)]

                for index in range(0, len(addl_fields)-1):
                    print(f'  "{addl_fields[index]:{max_field_width}s}: {addl_values[index]},', file=outfile)
                print(f'  "{addl_fields[len(addl_fields)-1]:{max_field_width}s}: {addl_values[len(addl_fields)-1]}', file=outfile)

        print('}]', file=outfile)

        if (export):
            infile.close()
            outfile.close()

# command-line testing
if (__file__ in sys.argv[0]):
  if (len(sys.argv) > 1):

      if (sys.argv[1] == "posts"):

          # set limit on number of posts to fetch / parse
          if (len(sys.argv) > 3 and sys.argv[3].isdigit()):
              limit = int(sys.argv[3])
              print(f"\nNote: limit provided ({limit}) is the *maximum* number of posts to be returned.")
              print(f"  Actual number returned may be < {limit} due to discussion posts being removed.")
          else:
              limit = None

          if (len(sys.argv) > 2):

              # fetch posts only
              if (sys.argv[2] == "fetch"):
                  print("\nFetching posts...\n")
                  posts(limit, True, False, False)

              # fetch and parse posts
              elif (sys.argv[2] == "parse"):
                  print("\nFetching and parsing posts...\n")
                  posts(limit, True, True, False)
                  
              # fetch, parse, and save posts to files
              elif (sys.argv[2] == "save"):
                  print("\nFetching, parsing, and saving posts...\n")
                  posts(limit, True, True, True)
          
          else:
              print("\n'posts' must be followed by 'fetch', 'parse', or 'save'")
              print("  and an optional number of posts, like 'posts fetch 3'")