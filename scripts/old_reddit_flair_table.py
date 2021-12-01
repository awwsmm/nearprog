from tools import reddit

#===============================================================================
#
#  script to print a markdown-formatted table of post flairs for old Reddit
#
#-------------------------------------------------------------------------------
#
#  run with
#    $ python3 path/to/old_reddit_flair_table.py
#
#===============================================================================

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

# get all currently-available post flairs
link_templates = reddit.nearprog().flair.link_templates
flairs = list(map(lambda x: x["text"], link_templates))

flairs.remove("Discussion")

baseurl = "https://old.reddit.com/r/nearprog/search?restrict_sr=on&q=flair%3A"

def makeurl(search_term):
    safe_term = search_term.replace(" ", "+").replace("&", "%26")
    return f"{baseurl}%22{safe_term}%22"

links = [mdlink(flair, makeurl(flair)) for flair in flairs]
format_table(links, 3)
