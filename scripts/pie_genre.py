import matplotlib.pyplot as plt
import json
from collections import Counter

with open('parsed.json') as f:
    posts = json.load(f)

counts = Counter([post['link_flair_text'] for post in posts])
ordered = counts.most_common()
keys, values = zip(*ordered)

fig1, ax1 = plt.subplots(figsize=(12, 9))

ax1.axis('equal')
ax1.pie(
    values[1:],
    labels = keys[1:],
    autopct='%1.1f%%',
    pctdistance=0.9,
    labeldistance=1.1)

plt.savefig('output/pie_genre.png', dpi=200)
#plt.show()
