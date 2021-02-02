import os, sys, json, re, pathlib
import praw # pip3 install praw

basedir = pathlib.Path(__file__).parent

#===============================================================================
#
#  methods for connecting to Reddit, and basic submission analysis
#
#-------------------------------------------------------------------------------
#
#  requires: a config.json file in the ../json directory, formatted like:
#
#             {
#               "client_id":     "Reddit API client ID",
#               "client_secret": "Reddit API client secret key",
#               "username":      "your Reddit username",
#               "password":      "your Reddit password"
#             }
#
#  to use this file in another file in this directory, add
#    import nearprog        # for other files in this directory
#    import tools.nearprog  # for files in the parent directory (scripts/)
#
#  ...to the top of the file, and get the subreddit object with
#    data = nearprog.get()
#
#  Then, you can loop over posts like (or similar):
#    for submission in data.top("month"):
#        # do something
#
#===============================================================================

def connect():
    with (basedir / '../../json/config.json').open('r') as f:
        config = json.load(f)

    reddit = praw.Reddit(
                 user_agent    = "nearprog_scraper by u/_awwsmm",
                 client_id     = config['client_id'],
                 client_secret = config['client_secret'],
                 username      = config['username'],
                 password      = config['password'])

    return reddit

def nearprog():
    return connect().subreddit("nearprog")

def submission_is_song(submission):
    return ((submission.link_flair_text != 'Discussion') and
            (submission.link_flair_text != 'Contest') and
            ('[Discussion]' not in submission.title))

def split_title(title):
    stripped = title.strip()
    # split the post title at " - " or " — " or " -- ", etc.
    # this gives us the artist at [0] and everything else at [2]
    split_title = re.split(' (-|—)+ ', stripped, 1) # only split 1 time
    artist = split_title[0]
    song = split_title[2]
    return (artist, song)
