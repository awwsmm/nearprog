import json
import fuzzy
import re
import utils

test_mode = False

def tests(arr):
    if (test_mode):
        print('')
        for elem in arr:
            print(elem,'=',eval(elem))

# try to extract (subgenre) in () instead of []
def parenthetical_subgenre(song):

    # try to parse (subgenre) like [subgenre]
    with open('genre_words.json') as f:
        genre_words = json.load(f)

    # return True if this word is a "genre word"
    def is_genre_word(word):
        return fuzzy.contains(genre_words, word)

    # extract "words" from any string
    # a "word" is any sequence of characters not including .-/, etc.
    def extract_words_from_string(str):
        return re.findall('[^ .-/,]+', str)

    # returns true if all words are "genre words"
    def all_genre_words(arr):
        return utils.all(arr, lambda x: is_genre_word(x))

    # find all (...) parenthetical expressions
    parentheticals = re.findall('\(([^(]+)\)', song)

    # by default, subgenre is empty string
    subgenre = ""

    if ('(' in song):
        maybe_genre = utils.filter(parentheticals, lambda x: all_genre_words(extract_words_from_string(x)))
        if (maybe_genre != []):
            subgenre = maybe_genre[0]

            limits = re.search('\s*\('+subgenre+'\)\s*', song)
            (start, end) = limits.span()
            song = song[:start] + song[end:]

    return (song, subgenre)

tests([
    'parenthetical_subgenre("Hello (It\'s Me)")',
    'parenthetical_subgenre("Goodbye (post-rock)")',
    'parenthetical_subgenre("Whaddup (post-jazz metal fusion / tango)")',
    'parenthetical_subgenre("(Sittin on the) Dock of the Bay")'
    ])
