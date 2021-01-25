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

# flatten an array of arrays, ex. [[1, 2], [3], [4, 5, 6]] => [1, 2, 3, 4, 5, 6]
def flatten(arrarr):
    return [item for sublist in arrarr for item in sublist]

tests([
    'flatten([[1, 2], [3], [4, 5, 6]])',
    'flatten([["Eminem"], ["Juice WRLD"]])'
    ])

# try to extract multiple artist names
def multiple_artists(artist):

    # split on " ft." / " feat."
    artists = re.split('\s+[Ff]eat.\s*|\s+[Ff]t.\s*', artist)

    # don't split artist names like "Black Country, New Road" and "Simon and Garfunkel"
    with open('compound_artists.json') as f:
        compound_artists = json.load(f)

    # split if not a compound artist
    def is_compound(artist):
        return fuzzy.contains(compound_artists, artist)

    # split on "and" except when followed by "the", like "Jim and the Other Guys"
    # split on ","
    def split_if_not_compound(artist):
        if (is_compound(artist)):
            return [artist]
        return re.split(',?\s+[Aa][Nn][Dd]\s+(?!the)|\s*,\s*', artist)

    return flatten(utils.foreach(artists, lambda x: split_if_not_compound(x)))

tests([
    'multiple_artists("Eminem ft. Juice WRLD")',
    'multiple_artists("Korn feat. Ice Cube")',
    'multiple_artists("Emanative feat. Ahu")',
    'multiple_artists("Flight Facilities feat. Broods, Reggie Watts, and Saro")',
    'multiple_artists("David Bowie feat. Maynard James Keenan and John Frusciante")',
    'multiple_artists("Intervals feat. Plini")',
    'multiple_artists("Flying Lotus feat. Kendrick Lamar")',
    'multiple_artists("Efterklang")',
    'multiple_artists("Dave Grohl, Trent Reznor, Josh Homme")',
    'multiple_artists("Black Country, New Road")',
    'multiple_artists("King Gizzard and the Lizard Wizard")',
    'multiple_artists("The Third and the Mortal")',
    'multiple_artists("Professor Caffeine and the Insecurities")',
    'multiple_artists("Simon and Garfunkel")'
    ])

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
    'parenthetical_subgenre("(Sittin on the) Dock of the Bay")',
    'parenthetical_subgenre("Pandora (Hardstyle)")',
    'parenthetical_subgenre("CERAMIC GIRL (Mathrock-Trap)")',
    'parenthetical_subgenre("Replicant (instrumental electronic)")',
    'parenthetical_subgenre("Chasing Suns (Alt Rock)")',
    'parenthetical_subgenre("Trust In Computers (psychedelic rock)")',
    'parenthetical_subgenre("Babel A.I. (Psytrance Metal Fusion)")',
    'parenthetical_subgenre("Euphoria (Electronic/Djent/Experimental)")',
    'parenthetical_subgenre("Cathedral of Pleasure (Electronic / Spokenword)")'
    ])
