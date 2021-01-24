#!/usr/bin/python

import json
import praw # pip3 install praw

# run with: python3 top_of_the_month.py
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

for submission in reddit.subreddit("nearprog").top("month"):
    print(f'{submission.score:3} | {submission.title}')
