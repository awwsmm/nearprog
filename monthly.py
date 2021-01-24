#!/usr/bin/python

import json
import praw # pip3 install praw
import datetime

# run with: python3 monthly.py
# requires: a config.json file in this directory, formatted like:
#             {
#               "client_id":     "Reddit API client ID",
#               "client_secret": "Reddit API client secret key",
#               "username":      "your Reddit username",
#               "password":      "your Reddit password"
#             }

with open('config.json') as f:
    config = json.load(f)

reddit = praw.Reddit(
             user_agent    = "nearprog_scraper by u/_awwsmm",
             client_id     = config['client_id'],
             client_secret = config['client_secret'],
             username      = config['username'],
             password      = config['password'])

dt = datetime.datetime.today()
counter = 1

with open('blacklist.json') as f:
    blacklist = json.load(f)

def is_blacklisted(artist, song):

    def fuzzy_intersection(given, blacklisted):
        given_lower = given.lower()
        blacklisted_lower = blacklisted.lower()
        return (given_lower in blacklisted_lower or blacklisted_lower in given_lower)

    for track in blacklist:
        if (fuzzy_intersection(artist, track['artist']) and fuzzy_intersection(song, track['song'])):
          return True;
    return False;

with open(f'monthly/{dt.year}-{dt.month:02}-{dt.day:02}.txt', 'w') as outfile:
    for submission in reddit.subreddit("nearprog").top("month"):
        if (submission.link_flair_text != 'Discussion'):
            title_parts = submission.title.split(' - ')
            artist = title_parts[0]
            song = title_parts[1]

            if (is_blacklisted(artist, song)):
                print(f' ---)  --^ | [[BLACKLISTED]] {submission.title}', file=outfile)
            else:
                print(f' {counter:3})  {submission.score:2}^ | {submission.title}', file=outfile)
                counter += 1
