
from urllib.parse import quote_plus

def mdlink(text, url):
    " format a markdown link "
    return f'[{text}]({url})'

def format_table(fields, columns=3):
    # table header
    print(' '.join(['|'] * (columns + 1)))
    print('-'.join(['|'] * (columns + 1)))
    # table rows
    for i in range(0, len(fields), columns):
        row = fields[i:i+columns]
        row += [''] * (columns - len(row))
        print('|', '|'.join(row), '|')
    

## TODO add PRAW support?

flairs = [
    "Acoustic & Flamenco",
    "Alt Metal",
    "Avant-Garde / Experimental",
    "Bluegrass",
    "Blues & Soul",
    "Classical / Orchestral",
    "Djent",
    "Doom / Stoner",
    "Electronic",
    "Folk / Country",
    "Funk",
    "Gothic Country",
    "House / EDM / Trap",
    "Indie / Alternative",
    "Industrial",
    "Jam Band",
    "Jazz / Big Band",
    "Math Rock",
    "Metal",
    "Metalcore / Hardcore",
    "New Wave",
    "Pop / Baroque Pop",
    "Post-Hardcore / Emo / Screamo",
    "Post-Punk",
    "Post-Rock",
    "Proto-Prog",
    "Psychedelic / Space Rock",
    "Punk & Grunge",
    "Rap & Hip Hop",
    "Rock",
    "Thrash & Death Metal",
    "Virtuoso Instrumentalist",
    "World / Traditional",
    "Surprise Me!",
]

baseurl = "https://old.reddit.com/r/nearprog/search?restrict_sr=on&q=flair%3A"
# Search only works on single words.
links = [mdlink(flair, baseurl + quote_plus(flair.split('/')[0].split()[0])) for flair in flairs]
format_table(links, 3)

