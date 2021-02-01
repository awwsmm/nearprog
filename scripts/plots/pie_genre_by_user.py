import matplotlib.pyplot as plt
import json
from collections import Counter
import sys

import parent # import parent directory scripts
import files  # ...which includes this

username = sys.argv[1]

with files.relopen('output/parsed.json') as f:
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

plt.savefig(parent.relpath(f'output/pie_genre_for_{username}.png'), dpi=100)
#plt.show()
