import os, sys, json, pathlib
import matplotlib.pyplot as plt
from collections import Counter

basedir = pathlib.Path(__file__).parent

#===============================================================================

username = sys.argv[1]

with (basedir / 'data/posts_parsed.json').open('r') as f:
    posts = json.load(f)

counts = Counter([post['link_flair_text'] for post in posts if post['author'] == username])
ordered = counts.most_common()
keys, values = zip(*ordered)

fig1, ax1 = plt.subplots(figsize=(12, 9))

ax1.axis('equal')
ax1.pie(
    values,
    labels = keys,
    autopct='%1.1f%%',
    pctdistance=0.9,
    labeldistance=1.1)

plt.savefig(basedir / f'plots/pie_genre_for_{username}.png', dpi=100)
#plt.show()
