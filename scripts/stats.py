#!/usr/bin/python

import nearprog
import datetime
import re # regular expressions
import fuzzy
import utils
import extract

# Usage:
#  1) fetch all data to a temporary file by setting fetch = True and running $ python3 stats.py
#  2) parse all data in the tmp file by setting fetch = False and running $ python3 stats.py

fetch = False

data = nearprog.get()

# fetch all submission titles and save to file
if (fetch):
    with open("tmp", 'w') as outfile:
        for submission in data.top("all", limit=None):
            if (submission.link_flair_text != 'Discussion' and '[Discussion]' not in submission.title):
                print(submission.title, file=outfile)

# parse submission titles from tmp file
else:
    with open("tmp", 'r') as infile:
        for title in infile:
            raw_title = title.strip()

            # split the post title at " - " or " — " or " -- ", etc.
            # this gives us the artist at [0] and everything else at [2]
            split_title = re.split(' (-|—)+ ', raw_title, 1) # only split 1 time
            artist = split_title[0]
            song = split_title[2]

            # extract the [subgenre] tag, if there is one
            subgenre = ""
            subgenre_match = re.search('\[.+\]', song)
            if (subgenre_match != None):
                (start, end) = subgenre_match.span()

                # song[end:] contains commentary after the [subgenre] -- remove
                song = (song[:start]).strip()
                subgenre = re.sub('[\[\]]', '', subgenre_match.group())

            # extract "junk" parentheticals like (live), (1998), etc.
            (song, junk) = extract.misc_parentheticals(song)

            # remove "" from around song title, if present
            if (song[0] == '"' and song[-1] == '"'):
                song = song[1:-1]

            # if no existing subgenre, try to extract (subgenre) in () instead of in []
            if (subgenre == ""):
                (new_song, subgenre) = extract.parenthetical_subgenre(song)

                # we inferred a subgenre
                if (subgenre != ""):
                    song = new_song
                    subgenre = subgenre

            # try to extract multiple artists separated by "," and "and"
            artists = extract.multiple_artists(artist)

            print('{')
            print(f'  "raw_title": "{raw_title}",')
            print(f'  "artists":   {artists},')
            print(f'  "song":      "{song}",')
            print(f'  "subgenre":  "{subgenre}"')
            print('}')




# all relevant fields
#for submission in data.top("all", limit=10): # None
#    print(index," :: ",submission.title," :: ",submission.created_utc," :: ",submission.link_flair_text," :: ",submission.score," :: ",submission.upvote_ratio," :: ",submission.author)
#    index += 1

