#!/usr/bin/python

import json
import datetime
import nearprog
import fuzzy

# run with: python3 monthly.py

dt = datetime.datetime.today()
counter = 1

with open('../json/banned_songs.json') as f:
    banned_songs = json.load(f)

def is_banned(artist, song):
    for track in banned_songs:
        if (fuzzy.match(artist, track['artist']) and fuzzy.match(song, track['song'])):
          return True;
    return False;

with open(f'../monthly/{dt.year}-{dt.month:02}-{dt.day:02}.txt', 'w') as outfile:
    for submission in nearprog.get().top("month"):
        if (submission.link_flair_text != 'Discussion'):
            title_parts = submission.title.split(' - ')
            artist = title_parts[0]
            song = title_parts[1]

            if (is_banned(artist, song)):
                print(f' ---)  --^ | [[BANNED]] {submission.title}', file=outfile)
            else:
                print(f' {counter:3})  {submission.score:2}^ | {submission.title}', file=outfile)
                counter += 1
