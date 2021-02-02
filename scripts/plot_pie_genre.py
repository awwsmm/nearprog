import os, json
import matplotlib.pyplot as plt
from collections import Counter

# get path relative to *this file*, not relative to user's current directory
def relpath (file):
    basedir = os.getcwd()
    scriptpath = __file__
    return os.path.abspath(os.path.join(basedir, scriptpath, '../', file))

with open(relpath('data/posts_parsed.json'), 'r') as f:
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

plt.savefig(relpath('plots/pie_genre.png'), dpi=100)
#plt.show()
