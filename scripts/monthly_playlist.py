import os, sys, json, re, datetime, pathlib, glob

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
#    $ python3 path/to/monthly_playlist.py
#
#  ...to save the playlist to a file, do
#    $ python3 path/to/monthly_playlist.py save
#
#===============================================================================

def playlist(test_mode = True):

    #---------------------------------------------------------------------------
    #  check if song appears in the last three months of playlists
    #---------------------------------------------------------------------------

    def read_to_string(filename):
        output = ""
        with open(filename) as file:
            output = file.read().replace('\n', '')
        return output

    # get the last three months (~90 days) of playlists, from most to least recent
    recent_files = sorted(glob.glob(str(basedir / f'../monthly_playlist/*.txt')), reverse=True)[:3]
    playlist_names = list(map(lambda x: x.rsplit('/', 1)[-1], recent_files))
    recent_playlists = list(map(lambda x: read_to_string(x), recent_files))

    def is_too_recent(title):
        for index in range(len(playlist_names)):
            if (title in recent_playlists[index]):
                return (True, index)
        return (False, -1)

    #---------------------------------------------------------------------------
    #  check if song appears in list of banned songs
    #---------------------------------------------------------------------------

    with (basedir / '../json/banned_songs.json').open('r') as f:
        banned_songs = json.load(f)

    def is_banned(artist, song):
        for track in banned_songs:
            if (extract.match(artist, track['artist']) and extract.match(song, track['song'])):
                return True
        return False

    #---------------------------------------------------------------------------
    #  loop over top songs from the past month, filtering as we go
    #---------------------------------------------------------------------------

    dt = datetime.datetime.today()

    if (test_mode):
        outfile = sys.stdout
    else:
        outfile = (basedir / f'../monthly_playlist/{dt.year}-{dt.month:02}-{dt.day:02}.txt').open('w')

    counter = 1
    for submission in reddit.nearprog().top("month"):
        if (reddit.submission_is_song(submission)):
            artist, song = reddit.split_title(submission.title)

            if (is_banned(artist, song)):
                print(f' ---)  --^ | [[BANNED]] {submission.title}', file=outfile)
            else:
                too_recent, playlist_index = is_too_recent(submission.title)
                if (too_recent):
                    print(f' ---)  --^ | [[RECENT]] ({playlist_names[playlist_index]}) {submission.title} ')
                else:
                    print(f' {counter:3})  {submission.score:2}^ | {submission.title}', file=outfile)
                    counter += 1

    if (not test_mode):
        outfile.close()

# command-line testing
if ("monthly_playlist.py" in sys.argv[0]):
    if (len(sys.argv) == 2 and sys.argv[1] == "save"):
        playlist(False)
    else:
        playlist(True)
