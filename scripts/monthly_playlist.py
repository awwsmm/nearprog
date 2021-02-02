import os, sys, json, re, datetime, pathlib

from tools import reddit
from tools import extract

basedir = pathlib.Path(__file__).parent

#===============================================================================
#
#  method to create monthly playlist
#
#-------------------------------------------------------------------------------
#
#  to test without writing the playlist to a file, do
#    $ python3 path/to/monthly_playlist.py test
#
#  ...to save the playlist to a file, drop the "test" argument
#
#===============================================================================

def playlist(test_mode):
    dt = datetime.datetime.today()

    if (test_mode):
        outfile = sys.stdout
    else:
        outfile = (basedir / f'../monthly_playlist/{dt.year}-{dt.month:02}-{dt.day:02}.txt').open('w')

    with (basedir / '../json/banned_songs.json').open('r') as f:
        banned_songs = json.load(f)

    def is_banned(artist, song):
        for track in banned_songs:
            if (extract.match(artist, track['artist']) and extract.match(song, track['song'])):
                return True
        return False

    counter = 1
    for submission in reddit.nearprog().top("month"):
        if (reddit.submission_is_song(submission)):
            artist, song = reddit.split_title(submission.title)

            if (is_banned(artist, song)):
                print(f' ---)  --^ | [[BANNED]] {submission.title}', file=outfile)
            else:
                print(f' {counter:3})  {submission.score:2}^ | {submission.title}', file=outfile)
                counter += 1

    if (not test_mode):
        outfile.close()

# command-line testing
if (len(sys.argv) == 2 and "monthly_playlist.py" in sys.argv[0] and sys.argv[1] == "test"):
    playlist(True)
else:
    playlist(False)