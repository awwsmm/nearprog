import sys
sys.path.extend(['..', '../src/modules'])

import json
from typing import List

from src.pull import Pull
from src.modules.core.submission import Submission
from src.modules.core.timestamp import Timestamp, day

# pull all available songs (last 1000)
pulled = Pull.songs(Timestamp.now() - 3*day) # (Timestamp.now() - 3*day) for last 3 days; (0) for all available songs (last 1000)

# sort newest -> oldest
new_songs: List[Submission] = sorted(pulled, key = lambda s: -s.timestamp)

# read in known songs
with open('../output/songs.json') as songs:
    songs: List[Submission] = list(map(lambda x: Submission.deserialise(x), json.load(songs)))

print(", ".join(map(lambda s: s.as_JSON(), songs)))
print(", ".join(map(lambda s: s.as_JSON(), new_songs)))

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
with open('../output/songs.json', 'w') as outfile:
    print("[", file=outfile)
    print(", ".join(map(lambda s: s.as_JSON(), sorted(songs, key = lambda s: -s.timestamp))), file=outfile)
    print("]", file=outfile)