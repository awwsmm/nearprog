import os, sys, json, re, pathlib
import praw # pip3 install praw

from typing import List, Tuple, Mapping
from praw import Reddit
from praw.models import Submission, Subreddit

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

def connect() -> praw.Reddit:
    with (basedir / '../../json/config.json').open('r') as f:
        config = json.load(f)

    reddit = praw.Reddit(
                 user_agent    = "nearprog_scraper by u/_awwsmm",
                 client_id     = config['client_id'],
                 client_secret = config['client_secret'],
                 username      = config['username'],
                 password      = config['password'])

    return reddit

def nearprog() -> Subreddit:
    """Returns a Subreddit instance for r/nearprog."""

    return connect().subreddit("nearprog")

def is_song(submission: Submission) -> bool:
    """Returns True if the given Submission is a song submission."""

    return ((submission.link_flair_text != 'Discussion') and
            (submission.link_flair_text != 'Contest') and
            (submission.link_flair_text != 'Announcement') and
            ('[Discussion]' not in submission.title))

def split_title(title: str) -> Tuple[str, str]:
    """Split the given post title at " - " or " — " or " -- ", etc."""

    stripped = title.strip()

    # this gives us the artist at [0] and everything else at [2]
    split_title = re.split(' (-|—)+ ', stripped, 1) # only split 1 time

    return (split_title[0], split_title[2]) # (artist, song)

def fetch_submissions_since(connection: Reddit, utc_timestamp: int) -> List[Submission]:
    """Return all r/nearprog submissions since the given UTC UNIX timestamp."""

    # Sort posts oldest -> newest, so oldest post is at head of list
    def fetch_n_most_recent_posts(n: int) -> List[Submission]:
        return sorted(list(connection.subreddit("nearprog").new(limit=n)),
            key = lambda x: x.created_utc)

    earliest_post_timestamp = utc_timestamp + 1
    fetch_multiplier = -1

    # To get all posts since <timestamp>, get the newest 100 posts and check the
    # 'created_utc' time of the earliest post. If it's not early enough, get the
    # next 100, 200, 400, etc. until the earliest post is earlier than 'since'.

    while (earliest_post_timestamp > utc_timestamp):
        fetch_multiplier += 1
        n_to_fetch = 2**fetch_multiplier * 100
        most_recent_posts = fetch_n_most_recent_posts(n_to_fetch)
        earliest_post_timestamp = most_recent_posts[0].created_utc

    # we now have a list of all submissions since the specified timestamp
    return [p for p in most_recent_posts if p.created_utc >= utc_timestamp]

def fetch_songs_since(connection: Reddit, utc_timestamp: int) -> List[Submission]:
    """Return all r/nearprog song submissions since the given UTC UNIX timestamp."""

    return [x for x in fetch_submissions_since(connection, utc_timestamp) if is_song(x)]

def defuzzed_submission_score(connection: Reddit, submission: Submission, iterations: int) -> float:
    """"De-fuzzes" a single submission's score by requesting the score from
       Reddit multiple times and returning the average."""

    score_sum = 0
    for _ in range(iterations):
        score_sum += connection.submission(submission.id).score
    return (score_sum / iterations)

def defuzzed_submissions_scores(connection: Reddit, submissions: List[Submission], iterations: int) -> Mapping[Submission, List[int]]:
    """"De-fuzzes" multiple submissions' scores by batch requesting each score
        from Reddit multiple times, and calculating the average score for each."""

    def t3_(id: str) -> str:
        if id.startswith('t3_'):
            return id
        else:
            return f't3_{id}'

    # scores is a dict mapping submission ids to lists of scores
    ids = [ t3_(submission.id) for submission in submissions ]
    scores = { i : list() for i in ids }

    for _ in range(iterations):
        for submission in connection.info(ids):
            scores[t3_(submission.id)].append(submission.score)

    # map given submissions to submission ids
    idmap = { t3_(submission.id) : submission for submission in submissions }
    return { idmap[i] : scores[i] for i in ids }