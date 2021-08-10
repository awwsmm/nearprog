import sys
sys.path.extend(['..', '../src/modules'])

import argparse
import json
from typing import List

from src.pull import Pull
from src.modules.core.submission import Submission
from src.modules.core.timestamp import Timestamp, day

def update(since: int, limit: int):

    # pull submissions (max 1000)
    pulled = Pull.songs(since, limit)

    # sort newest -> oldest
    new_songs: List[Submission] = sorted(pulled, key = lambda s: -s.timestamp)

    # output file
    songs_json = '../output/songs.json'

    # read in known songs
    with open(songs_json) as songs:
        songs: List[Submission] = list(map(lambda x: Submission.deserialise(x), json.load(songs)))

    # use timestamps as primary keys
    timestamps = list(map(lambda song: song.timestamp, songs))

    # update known songs and add new songs
    for song in new_songs:

        # if we already know about this song, update it with the new data we've fetched
        try:
            index = timestamps.index(song.timestamp)
            songs[index] = song

        # if this song is new to us, add it to the list of known songs
        except:
            songs.append(song)

    # rewrite the "known songs" file
    with open(songs_json, 'w') as outfile:
        print("[", file=outfile)
        print(", ".join(map(lambda s: s.as_JSON(), sorted(songs, key = lambda s: -s.timestamp))), file=outfile)
        print("]", file=outfile)
        print(f'{songs_json} has been updated')

# command-line interface
if ("update_songs.py" in sys.argv[0]):

    desc = "Script to pull and parse recent submissions to r/nearprog."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-d", dest = "days", type = int, default = 3,
        help = "days of submissions to fetch from today backward (default: 3)")

    parser.add_argument('-m', dest = "max", type = int, default = 1000,
        help = "maximum number of submissions to fetch from Reddit (default: 1000, oldest are returned first)")

    args = parser.parse_args()
    update(Timestamp.now() - args.days*day, args.max)