import os, sys, json, re

from tools import reddit
from tools import extract

#===============================================================================
#
#  utilities
#
#===============================================================================

# open file relative to *this file*, not relative to user's current directory
def relopen (file, rw='r'):
    basedir = os.getcwd()
    scriptpath = __file__
    filepath = os.path.abspath(os.path.join(basedir, scriptpath, '../', file))
    return open(filepath, rw)

#===============================================================================
#
#  methods to pull / parse different data from Reddit
#
#-------------------------------------------------------------------------------
#
#  to test *fetching* posts / submissions from Reddit, do
#    $ python3 path/to/pull_data.py posts fetch [N]
#
#  ...where [N] is the maximum number of posts to fetch. (Note that the number
#  of fetched posts will probably be < N because of removed Discussion posts.)
#  This will not save any posts to an output file, but only print them to the
#  terminal, un-processed.
#
#  N is optional, and if unset, all available posts will be fetched from Reddit.
#
#  to test *parsing* posts / submissions from Reddit, do
#    $ python3 path/to/pull_data.py posts parse [N]
#
#  to pull and parse posts and save to raw and parsed output files, do
#    $ python3 path/to/pull_data.py posts save [N]
#
#-------------------------------------------------------------------------------
#
#  to test fetching traffic data from Reddit, do
#    $ python3 path/to/pull_data.py traffic
#
#  to fetch traffic data and save to an output file, do
#    $ python3 path/to/pull_data.py traffic save
#
#===============================================================================

# fetch and parse post data
def posts(limit = None, fetch = True, parse = True, export = True):
    data = reddit.nearprog()

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
        def get_fields(submission):
            return list(map(lambda x: str(getattr(submission, x)), fields))
            
        # fetch post fields and separate with double semicolons (;;)
        all_posts = data.top("all", limit=limit)
        song_posts = filter(lambda x: reddit.submission_is_song(x), all_posts)
        fetched_posts = [";;".join(get_fields(post)) for post in song_posts]

        # export to output file as optional side effect
        if (export):
            with relopen(out_raw, 'w') as outfile:
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
            infile = relopen(out_raw, 'r')
            outfile = relopen(out_parsed, 'w')
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

# fetch and save traffic data
def traffic(export = True):

    out = "data/traffic.json"

    if (export):
        outfile = relopen(out, 'w')
    else:
        outfile = sys.stdout
        
    # traffic is *much* easier as it's already json formatted
    # ...and requires no parsing

    data = reddit.nearprog()
    traffic = data.traffic()

    print(json.dumps(traffic), file=outfile)

    if (export):
        outfile.close()

# command-line testing
if (len(sys.argv) > 1 and "pull_data.py" in sys.argv[0]):

    if (sys.argv[1] == "posts"):

        # set limit on number of posts to fetch / parse
        if (len(sys.argv) > 3 and sys.argv[3].isdigit()):
            limit = int(sys.argv[3])
        else:
            limit = None

        if (len(sys.argv) > 2):

            # fetch posts only
            if (sys.argv[2] == "fetch"):
                print("\nfetching posts...\n")
                posts(limit, True, False, False)

            # fetch and parse posts
            elif (sys.argv[2] == "parse"):
                print("\nfetching and parsing posts...\n")
                posts(limit, True, True, False)
                
            # fetch, parse, and save posts to files
            elif (sys.argv[2] == "save"):
                print("\nfetching, parsing, and saving posts...\n")
                posts(limit, True, True, True)

    elif (sys.argv[1] == "traffic"):
        if (len(sys.argv) > 2 and sys.argv[2] == "save"):
            print("\nfetching and saving traffic data...\n")
            traffic(True)
        else:
            print("\nfetching traffic data...\n")
            traffic(False)
