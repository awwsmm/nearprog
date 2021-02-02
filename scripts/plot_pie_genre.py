import os, json, pathlib
import matplotlib.pyplot as plt
from collections import Counter

basedir = pathlib.Path(__file__).parent

#===============================================================================

with (basedir / 'data/posts_parsed.json').open('r') as f:
    posts = json.load(f)

counts = Counter([post['link_flair_text'] for post in posts])
ordered = counts.most_common()
keys, values = zip(*ordered)

# remove "Surprise Me!" tag
index = keys.index("Surprise Me!")
keys = keys[:index] + keys[index+1:]
values = values[:index] + values[index+1:]

fig1, ax1 = plt.subplots(figsize=(12, 9))

ax1.axis('equal')
ax1.pie(
    values,
    labels = keys,
    autopct='%1.1f%%',
    pctdistance=0.9,
    labeldistance=1.05)

plt.savefig(basedir / 'plots/pie_genre.png', dpi=100)
#plt.show()
