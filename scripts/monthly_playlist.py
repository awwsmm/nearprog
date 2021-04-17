import os, sys, json, re, datetime, pathlib, glob, argparse
import praw

from praw import Reddit
from praw.models import Submission

from tools import reddit
from tools import extract
from typing import List, Tuple, Mapping, TypeVar

T = TypeVar("T")

basedir = pathlib.Path(__file__).parent

# TODO add 'until' as well as since?
#      will require disabling removing songs which appear in older playlists

def top_songs(n: int, since: int, defuzz_iterations: int) -> List[Tuple[Submission, float]]:
    """Returns the top n song Submissions posted since the cutoff time.

    Songs are filtered out and removed if they appear in recent monthly
    playlists, or if they are in the list of banned songs.

    1608937131 is the minimum allowable cutoff time, as it is the UTC UNIX
    timestamp of the first submission posted to r/nearprog:
    https://www.reddit.com/r/nearprog/comments/kk7pnh/spidergawd_empty_rooms_stoner_rock/

    Args:
      n:
        Maximum number of songs to return (maximum length of the playlist).
      since:
        The earliest allowed Submission created_utc UNIX timestamp.
      defuzz_iterations:
        The number of times to request the score of each Submission, in order to
        undo Reddit's "score fuzzing" by finding the average score.

    Returns:
      A dict mapping Submissions to their "de-fuzzed" scores, sorted high-to-low by score.
    """

    if (n < 1):
        raise ValueError(f"'n' must be > 0")

    if (since < 1608937131):
        raise ValueError(f"'since' must be >= 1608937131 (the timestamp of r/nearprog's first post)")

    if (defuzz_iterations < 2):
        raise ValueError(f"'defuzz_iterations' must be >= 2")

    dtobj = datetime.datetime.utcfromtimestamp(since)
    print("\nFinding top songs posted to r/nearprog since " + dtobj.strftime('%Y-%m-%d %H:%M:%S'))
    print(f"Returning {n} songs, with scores defuzzed {defuzz_iterations} times...")

    connection = reddit.connect()

    # fetch all song submissions since the given UTC UNIX timestamp
    posts: List[Submission] = reddit.fetch_songs_since(connection, since)

    # helper method to remove indices from a list in reverse order
    def remove_indices(items: List[T], indices: List[int]) -> List[T]:
        indices = sorted(indices, reverse=True)
        for index in indices:
            items.pop(index)
        return items

    #---------------------------------------------------------------------------
    #  if any song appears in a recent playlist, warn the user, and remove it
    #---------------------------------------------------------------------------

    def read_playlist_file(filename: str) -> str:
        output = ""
        with open(filename, encoding='utf-8') as file:
            output = file.read().replace('\n', '')
        return output

    # get the last three months (~90 days) of playlists, from most to least recent
    recent_files = sorted(glob.glob(str(basedir / f'../monthly_playlist/*.txt')), reverse=True)[:3]
    playlist_names = list(map(lambda x: x.rsplit('/', 1)[-1], recent_files))
    recent_playlists = list(map(lambda x: read_playlist_file(x), recent_files))

    # check if the post title appears exactly as-is in any recent playlist
    def is_too_recent(post: Submission) -> Tuple[bool, int]:
        for index in range(len(playlist_names)):
            if (post.title in recent_playlists[index]):
                return (True, index)
        return (False, -1)

    # warn the user, and remove songs that appear in recent playlists
    def remove_recent_songs(posts: List[Submission]) -> List[Submission]:
        indices = []
        for i in range(len(posts)):
            post = posts[i]
            too_recent, index = is_too_recent(post)
            if (too_recent):
                print(f" ! REMOVED (Appears in '{playlist_names[index]}'): '{post.title}'.")
                indices.append(i)
        return remove_indices(posts, indices)

    posts = remove_recent_songs(posts)

    #---------------------------------------------------------------------------
    #  if any song appears in the list of banned songs, warn and remove it
    #---------------------------------------------------------------------------

    with (basedir / '../json/banned_songs.json').open('r', encoding='utf-8') as f:
        banned_songs = json.load(f)

    def is_banned(artist, song):
        for track in banned_songs:
            if (extract.match(artist, track['artist']) and extract.match(song, track['song'])):
                return True
        return False

    # warn the user, and remove songs that appear in the banned songs list
    def remove_banned_songs(posts: List[Submission]) -> List[Submission]:
        indices = []
        for i in range(len(posts)):
            post = posts[i]
            artist, song = reddit.split_title(post.title)
            if (is_banned(artist, song)):
                print(f" ! REMOVED (Banned): '{post.title}'.")
                indices.append(i)
        return remove_indices(posts, indices)

    posts = remove_banned_songs(posts)

    #---------------------------------------------------------------------------
    #  get defuzzed post scores for the remaining songs
    #---------------------------------------------------------------------------

    def defuzzed_scores(submissions: List[Submission]) -> Mapping[Submission, List[int]]:
        return reddit.defuzzed_submissions_scores(connection, submissions, defuzz_iterations)

    posts_and_scores = { post : sum(scores)/len(scores) for post, scores in defuzzed_scores(posts).items() }

    # sort posts by their defuzzed scores, high -> low, and return
    return sorted(posts_and_scores.items(), key = lambda x: x[1], reverse = True)[:n]

def print_top_songs(n: int = 60, since: int = 1608937131, defuzz_iterations: int = 5, export = False):
    start = datetime.datetime.today()
    posts_and_scores = top_songs(n, since, defuzz_iterations)
    end = datetime.datetime.today()

    if (export):
        outfile = (basedir / f'../monthly_playlist/{start.year}-{start.month:02}-{start.day:02}.txt').open('w', encoding='utf-8')
    else:
        outfile = sys.stdout
        print("") # skip a line for easier readability

    top50 = sorted(posts_and_scores[:50], key = lambda ps: int(ps[0].created_utc))

    print(f"playlist generated at {int((start - datetime.datetime(1970, 1, 1)).total_seconds())}, in {(end-start).seconds} seconds, showing {n} submissions max", file=outfile)
    print(f"         posted since {since}, with {defuzz_iterations} defuzz iterations.", file=outfile)
    print(f"Newest song posted at {int(top50[-1][0].created_utc)} (in top 50 posts) ('{top50[-1][0].title}').", file=outfile)
    print(f"Oldest song posted at {int(top50[0][0].created_utc)} (in top 50 posts) ('{top50[0][0].title}').\n", file=outfile)

    counter = 1
    for submission, score in posts_and_scores:
        print(f' {counter:3})  {score:4.1f}^ | {submission.title}', file=outfile)
        counter += 1

    if (export):
        outfile.close()

# command-line testing
if ("monthly_playlist.py" in sys.argv[0]):

    desc = "Returns the top 'n' submissions posted at or after the cutoff time."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-n', dest="num", type=int, default=60,
        help="maximum [n]umber of songs to return: default 60, minimum 60")

    parser.add_argument('-t', dest="since", type=int, default=0,
        help="minimum allowed UTC UNIX [t]imestamp for submissions: default 1608937131, minimum 1608937131")

    parser.add_argument('-i', dest="defuzz_iterations", type=int, default=5,
        help="number of defuzzing [i]terations: default 5, minimum 2")

    parser.add_argument('-s', dest="save", action='store_true',
        help="[s]ave the playlist to a TXT file")

    args = parser.parse_args()
    print_top_songs(max(60, args.num), max(1608937131, args.since), max(2, args.defuzz_iterations), args.save)