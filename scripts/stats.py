#!/usr/bin/python

import nearprog
import datetime
import re # regular expressions
import fuzzy
import utils
import extract
import json

# Usage:
#  1) fetch all data to a temporary file by setting fetch = True and running $ python3 stats.py
#  2) parse all data in the tmp file by setting fetch = False and running $ python3 stats.py

fetch = False
limit = None

data = nearprog.get()

fields = ["title", "created_utc", "link_flair_text", "score", "upvote_ratio", "author"]
max_field_width = max(len(max(fields, key=len)), len("raw_title")) + 2
types = ["str", "float", "str", "int", "float", "str"]

# fetch all submission titles and save to double-semicolon-separated variables file (a;;b;;c)
if (fetch):
    with open("tmp", 'w') as outfile:
        def print_to_tmp(submission):
            row = ""
            for field in fields:
                row = row + str(eval(f"submission.{field}")) + ";;"
            print(row[:-2], file=outfile)

        for submission in data.top("all", limit=limit):
            if (submission.link_flair_text != 'Discussion' and '[Discussion]' not in submission.title):
                print_to_tmp(submission)

# parse submission titles from tmp file
else:
    with open("tmp", 'r') as infile, open("out", 'w') as outfile:

        # open the JSON object for the first post
        print('[{', file=outfile)

        # write a "}, {" before every entry except the first
        first_row = True

        for row in infile:
            if (first_row == False):
                print("}, {", file=outfile)
            first_row = False

            # split the input into field values
            field_values = row.split(";;")

            # write the non-title fields (we'll parse "title" below)
            for field in fields:
                if (field != "title"):
                    type = types[fields.index(field)]
                    field_value = field_values[fields.index(field)]
                    if (type == "str"):
                        field_value = '"' + field_value.strip() + '"'
                    else:
                        field_value = eval(f'{type}(field_value)')
                    field += '"'
                    print(f'  "{field:{max_field_width}s}: {field_value},', file=outfile)

            # if tmp file contains a "title" field, try to parse it
            if ("title" in fields):
                title = field_values[fields.index("title")]
                raw_title = title.strip() # .replace('\n', '').replace('\r', '').replace('\t', ' ')

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
                artists = json.dumps(extract.multiple_artists(artist))

                addl_fields = ["raw_title\"", "artists\"", "song\"", "subgenre\""]
                addl_values = [json.dumps(raw_title.strip()), artists, json.dumps(song), json.dumps(subgenre)]

                for index in range(0, len(addl_fields)-1):
                    print(f'  "{addl_fields[index]:{max_field_width}s}: {addl_values[index]},', file=outfile)
                print(f'  "{addl_fields[len(addl_fields)-1]:{max_field_width}s}: {addl_values[len(addl_fields)-1]}', file=outfile)

        print('}]', file=outfile)




# all relevant fields
#for submission in data.top("all", limit=10): # None
#    print(index," :: ",submission.title," :: ",submission.created_utc," :: ",submission.link_flair_text," :: ",submission.score," :: ",submission.upvote_ratio," :: ",submission.author)
#    index += 1

