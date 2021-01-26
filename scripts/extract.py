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
    with open('../json/compound_artists.json') as f:
        compound_artists = json.load(f)

    # split if not a compound artist
    def is_compound(artist):
        return fuzzy.contains(compound_artists, artist)

    # split on "and" except when followed by "the", like "Jim and the Other Guys"
    # split on ",", "+", "&"
    # split on " X " or " x "
    # split on " with "
    def split_if_not_compound(artist):
        if (is_compound(artist)):
            return [artist]
        return re.split(',?\s+[Aa][Nn][Dd]\s+(?![Tt][Hh][Ee])|\s*[,+&]\s*|\s+[Xx]\s+|\s+with\s+', artist)

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
    'multiple_artists("King Gizzard And The Lizard Wizard")',
    'multiple_artists("The Third and the Mortal")',
    'multiple_artists("Professor Caffeine and the Insecurities")',
    'multiple_artists("Simon and Garfunkel")',
    'multiple_artists("Jess & the Ancient Ones")',
    'multiple_artists("Maps & Atlases")',
    'multiple_artists("Yuki Koshimoto & Liam Tillyer")',
    'multiple_artists("Yussef Dayes X Alfa Mist")',
    'multiple_artists("Jeremy Flower with Carla Kihlstedt")'
    ])

# try to extract (subgenre) in () instead of []
def parenthetical_subgenre(song):

    # try to parse (subgenre) like [subgenre]
    with open('../json/genre_words.json') as f:
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

# try to extract miscellaneous parentheticals (dates, "live", etc.)
def misc_parentheticals(song):

    # extract all (...) parenthetical expressions like...
    live = "\s*\([Ll][Ii][Vv][Ee][^(]*\)\s*"    # (Live), (live), (Live at...), etc.
    year = "\s*\(19[0-9]{2}[^(]*\)\s*|\s*\(20[0-9]{2}[^(]*\)\s*" # (1995), (2001), (2004, Los Angeles), etc.
    warn = "\s*\([Ww][Aa][Rr][Nn][Ii][Nn][Gg][^(]*\)\s*" # (WARNING...), (warning...), etc.

    # extract anything within paired tildes ~...~
    tilded = "\s*~[^~]+~\s*"

    parentheticals = re.findall(live+"|"+year+"|"+warn+"|"+tilded, song)

    if (parentheticals == []):
        return (song, [])

    for str in parentheticals:
        start = song.find(str)
        end = start + len(str)
        song = song[:start] + song[end:]

    return (song, parentheticals)

tests([
    'misc_parentheticals("No parentheses in here!")',
    'misc_parentheticals("Big Love (Live)")',
    'misc_parentheticals("Big Love (Not Live)")',
    'misc_parentheticals("(Hello) Goodbye")',
    'misc_parentheticals("Hello (Goodbye)")',
    'misc_parentheticals("Vajra (Live at the Ace of Spades, Sacramento Ca. 8/29/17)")',
    'misc_parentheticals("\\\"Mongol Hiimori\\\" (2014, Mongolia)")',
    'misc_parentheticals("Page 125 / What Would You Do? / Help Father Sun (1972)")',
    'misc_parentheticals("Live Jam From The Noita Game Soundtrack Recording (2018)")',
    'misc_parentheticals("On Tuesday (1987)")',
    'misc_parentheticals("O\'er Hell and Hide (2006)")',
    'misc_parentheticals("DMC World DJChampionship 2005 live set (Remixed, DJ set) <3")',
    'misc_parentheticals("Lindsay Buckingham (Fleetwood Mac)")',
    'misc_parentheticals("Test (live) (2018)")',
    'misc_parentheticals("(live) Test (1998)")',
    'misc_parentheticals("Triple Agent - Explorer ~Bad Tango remix~")'
    ])
