import os, sys, json, re, pathlib

basedir = pathlib.Path(__file__).parent

#===============================================================================
#
#  utilities and testing
#
#  to run tests, execute the following command in the terminal:
#    $ python3 path/to/extract.py test
#
#===============================================================================

if (len(sys.argv) > 1 and "extract.py" in sys.argv[0] and sys.argv[1] == "test"):
    print("testing extract.py")
    test_mode = True
else: 
    test_mode = False

def tests(arr):
    if (test_mode):
        print('')
        for expr, expected in arr:
            actual = eval(expr)
            if (str(actual) == str(expected)):
                print(f"  ✅ {expr} == {expected}")
            else:
                print(f"  ❌ {expr} != {expected}")
                print(f"      found: {actual}")

# flatten an array of arrays, ex. [[1, 2], [3], [4, 5, 6]] => [1, 2, 3, 4, 5, 6]
def flatten(arrarr):
    return [item for sublist in arrarr for item in sublist]

tests([
    ('flatten([[1, 2], [3], [4, 5, 6]])', '[1, 2, 3, 4, 5, 6]'),
    ('flatten([["Eminem"], ["Juice WRLD"]])', "['Eminem', 'Juice WRLD']")
    ])

#===============================================================================
#
#  methods for fuzzy matching
#
#===============================================================================

# used to test that "Styx" == "styx", etc.
def match(a, b):
    a_lower = a.lower()
    b_lower = b.lower()
    return (a_lower in b_lower or b_lower in a_lower)

tests([
    ('match("dog", "dog")',                  True  ),
    ('match("dog", "Dog!")',                 True  ),
    ('match("Dog", "? dog ")',               True  ),
    ('match("Dog", "I have a DOG")',         True  ),
    ('match("cat", "dog")',                  False ),
    ('match("cat", "I love cats and dogs")', True  )
    ])

def contains(array, elem):
    return any(match(arrelem, elem) for arrelem in array)

arr = ["dog", "hello i am a CAT", "dogs and cats"]
tests([
    ('contains('+ str(arr) +', "DOG")',  True  ),
    ('contains('+ str(arr) +', "cat")',  True  ),
    ('contains('+ str(arr) +', "frog")', False )
    ])

#===============================================================================
#
#  methods to extract information from post titles
#
#===============================================================================

# try to extract multiple artist names
def multiple_artists(artist):

    # split on " ft." / " feat."
    artists = re.split(r'\s+[Ff]eat.\s*|\s+[Ff]t.\s*', artist)

    # don't split artist names like "Black Country, New Road" and "Simon and Garfunkel"
    with (basedir / '../../json/compound_artists.json').open('r') as f:
        compound_artists = json.load(f)

    # split if not a compound artist
    def is_compound(artist):
        return contains(compound_artists, artist)

    # split on "and" except when followed by "the", like "Jim and the Other Guys"
    # split on ",", "+", "&"
    # split on " X " or " x "
    # split on " with "
    def split_if_not_compound(artist):
        if (is_compound(artist)):
            return [artist]
        return re.split(r',?\s+[Aa][Nn][Dd]\s+(?![Tt][Hh][Ee])|\s*[,+&]\s*|\s+[Xx]\s+|\s+with\s+', artist)

    return flatten(list(map(lambda x: split_if_not_compound(x), artists)))

tests([
    ('multiple_artists("Eminem ft. Juice WRLD")', "['Eminem', 'Juice WRLD']"),
    ('multiple_artists("Korn feat. Ice Cube")', "['Korn', 'Ice Cube']"),
    ('multiple_artists("Emanative feat. Ahu")', "['Emanative', 'Ahu']"),
    ('multiple_artists("Flight Facilities feat. Broods, Reggie Watts, and Saro")',
        "['Flight Facilities', 'Broods', 'Reggie Watts', 'Saro']"),
    ('multiple_artists("David Bowie feat. Maynard James Keenan and John Frusciante")',
        "['David Bowie', 'Maynard James Keenan', 'John Frusciante']"),
    ('multiple_artists("Intervals feat. Plini")', "['Intervals', 'Plini']"),
    ('multiple_artists("Flying Lotus feat. Kendrick Lamar")', "['Flying Lotus', 'Kendrick Lamar']"),
    ('multiple_artists("Efterklang")', "['Efterklang']"),
    ('multiple_artists("Dave Grohl, Trent Reznor, Josh Homme")', "['Dave Grohl', 'Trent Reznor', 'Josh Homme']"),
    ('multiple_artists("Black Country, New Road")', "['Black Country, New Road']"),
    ('multiple_artists("King Gizzard and the Lizard Wizard")', "['King Gizzard and the Lizard Wizard']"),
    ('multiple_artists("King Gizzard And The Lizard Wizard")', "['King Gizzard And The Lizard Wizard']"),
    ('multiple_artists("The Third and the Mortal")', "['The Third and the Mortal']"),
    ('multiple_artists("Professor Caffeine and the Insecurities")', "['Professor Caffeine and the Insecurities']"),
    ('multiple_artists("Simon and Garfunkel")', "['Simon and Garfunkel']"),
    ('multiple_artists("Jess & the Ancient Ones")', "['Jess & the Ancient Ones']"),
    ('multiple_artists("Maps & Atlases")', "['Maps & Atlases']"),
    ('multiple_artists("Yuki Koshimoto & Liam Tillyer")', "['Yuki Koshimoto', 'Liam Tillyer']"),
    ('multiple_artists("Yussef Dayes X Alfa Mist")', "['Yussef Dayes', 'Alfa Mist']"),
    ('multiple_artists("Jeremy Flower with Carla Kihlstedt")', "['Jeremy Flower', 'Carla Kihlstedt']")
    ])

# try to extract (subgenre) in () instead of []
def parenthetical_subgenre(song):

    # try to parse (subgenre) like [subgenre]
    with (basedir / '../../json/genre_words.json').open('r') as f:
        genre_words = json.load(f)

    # return True if this word is a "genre word"
    def is_genre_word(word):
        return contains(genre_words, word)

    # extract "words" from any string
    # a "word" is any sequence of characters not including .-/, etc.
    def extract_words_from_string(str):
        return re.findall('[^ .-/,]+', str)

    # returns true if all words are "genre words"
    def all_genre_words(arr):
        return all(map(lambda x: is_genre_word(x), arr))

    # find all (...) parenthetical expressions
    parentheticals = re.findall(r'\(([^(]+)\)', song)

    # by default, subgenre is empty string
    subgenre = ""

    if ('(' in song):
        maybe_genre = list(filter(lambda x: all_genre_words(extract_words_from_string(x)), parentheticals))
        if (maybe_genre != []):
            subgenre = maybe_genre[0]

            limits = re.search(r'\s*\('+subgenre+r'\)\s*', song)
            (start, end) = limits.span()
            song = song[:start] + song[end:]

    return (song, subgenre)

tests([
    ('parenthetical_subgenre("Hello (It\'s Me)")', "(\"Hello (It's Me)\", '')"),
    ('parenthetical_subgenre("Goodbye (post-rock)")', "('Goodbye', 'post-rock')"),
    ('parenthetical_subgenre("Whaddup (post-jazz metal fusion / tango)")',
        "('Whaddup', 'post-jazz metal fusion / tango')"),
    ('parenthetical_subgenre("(Sittin on the) Dock of the Bay")', "('(Sittin on the) Dock of the Bay', '')"),
    ('parenthetical_subgenre("Pandora (Hardstyle)")', "('Pandora', 'Hardstyle')"),
    ('parenthetical_subgenre("CERAMIC GIRL (Mathrock-Trap)")', "('CERAMIC GIRL', 'Mathrock-Trap')"),
    ('parenthetical_subgenre("Replicant (instrumental electronic)")', "('Replicant', 'instrumental electronic')"),
    ('parenthetical_subgenre("Chasing Suns (Alt Rock)")', "('Chasing Suns', 'Alt Rock')"),
    ('parenthetical_subgenre("Trust In Computers (psychedelic rock)")', "('Trust In Computers', 'psychedelic rock')"),
    ('parenthetical_subgenre("Babel A.I. (Psytrance Metal Fusion)")', "('Babel A.I.', 'Psytrance Metal Fusion')"),
    ('parenthetical_subgenre("Euphoria (Electronic/Djent/Experimental)")',
        "('Euphoria', 'Electronic/Djent/Experimental')"),
    ('parenthetical_subgenre("Cathedral of Pleasure (Electronic / Spokenword)")', 
        "('Cathedral of Pleasure', 'Electronic / Spokenword')")
    ])

# try to extract miscellaneous parentheticals (dates, "live", etc.)
def misc_parentheticals(song):

    # extract all (...) parenthetical expressions like...
    live = r"\s*\([Ll][Ii][Vv][Ee][^(]*\)\s*"    # (Live), (live), (Live at...), etc.
    year = r"\s*\(19[0-9]{2}[^(]*\)\s*|\s*\(20[0-9]{2}[^(]*\)\s*" # (1995), (2001), (2004, Los Angeles), etc.
    warn = r"\s*\([Ww][Aa][Rr][Nn][Ii][Nn][Gg][^(]*\)\s*" # (WARNING...), (warning...), etc.
    rip  = r"\s*\([Rr]\.?[Ii]\.?[Pp]\.?\)\s*"

    # extract anything within paired tildes ~...~
    tilded = r"\s*~[^~]+~\s*"

    parentheticals = re.findall(live+"|"+year+"|"+warn+"|"+rip+"|"+tilded, song)

    if (parentheticals == []):
        return (song, [])

    for str in parentheticals:
        start = song.find(str)
        end = start + len(str)
        song = song[:start] + song[end:]

    return (song, parentheticals)

tests([
    ('misc_parentheticals("No parentheses in here!")', "('No parentheses in here!', [])"),
    ('misc_parentheticals("Big Love (Live)")', "('Big Love', [' (Live)'])"),
    ('misc_parentheticals("Big Love (Not Live)")', "('Big Love (Not Live)', [])"),
    ('misc_parentheticals("(Hello) Goodbye")', "('(Hello) Goodbye', [])"),
    ('misc_parentheticals("Hello (Goodbye)")', "('Hello (Goodbye)', [])"),
    ('misc_parentheticals("Vajra (Live at the Ace of Spades, Sacramento Ca. 8/29/17)")',
        "('Vajra', [' (Live at the Ace of Spades, Sacramento Ca. 8/29/17)'])"),
    ('misc_parentheticals("\\\"Mongol Hiimori\\\" (2014, Mongolia)")',
        "('\"Mongol Hiimori\"', [' (2014, Mongolia)'])"),
    ('misc_parentheticals("Page 125 / What Would You Do? / Help Father Sun (1972)")',
        "('Page 125 / What Would You Do? / Help Father Sun', [' (1972)'])"),
    ('misc_parentheticals("Live Jam From The Noita Game Soundtrack Recording (2018)")',
        "('Live Jam From The Noita Game Soundtrack Recording', [' (2018)'])"),
    ('misc_parentheticals("On Tuesday (1987)")', "('On Tuesday', [' (1987)'])"),
    ('misc_parentheticals("O\'er Hell and Hide (2006)")', "(\"O'er Hell and Hide\", [' (2006)'])"),
    ('misc_parentheticals("DMC World DJChampionship 2005 live set (Remixed, DJ set) <3")',
        "('DMC World DJChampionship 2005 live set (Remixed, DJ set) <3', [])"),
    ('misc_parentheticals("Lindsay Buckingham (Fleetwood Mac)")',
        "('Lindsay Buckingham (Fleetwood Mac)', [])"),
    ('misc_parentheticals("Test (live) (2018)")', "('Test', [' (live) ', '(2018)'])"),
    ('misc_parentheticals("(live) Test (1998)")', "('Test', ['(live) ', ' (1998)'])"),
    ('misc_parentheticals("Triple Agent - Explorer ~Bad Tango remix~")',
        "('Triple Agent - Explorer', [' ~Bad Tango remix~'])"),
    ('misc_parentheticals("SOPHIE (RIP)")', "('SOPHIE', [' (RIP)'])")
    ])
