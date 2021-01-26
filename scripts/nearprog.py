#!/usr/bin/python

import json
import praw # pip3 install praw

# to use in another file in this directory, add
#     import nearprog
#
# ...to the top of the file, and get the subreddit object with
#     data = nearprog.get()
#
# Then, you can loop over posts like (or similar):
#     for submission in data.top("month"):
#         # do something

# requires: a config.json file in the ../json directory, formatted like:
#             {
#               "client_id":     "Reddit API client ID",
#               "client_secret": "Reddit API client secret key",
#               "username":      "your Reddit username",
#               "password":      "your Reddit password"
#             }

def get():
    with open('../json/config.json') as f:
        config = json.load(f)

    reddit = praw.Reddit(
                 user_agent    = "nearprog_scraper by u/_awwsmm",
                 client_id     = config['client_id'],
                 client_secret = config['client_secret'],
                 username      = config['username'],
                 password      = config['password'])

    return reddit.subreddit("nearprog")
