import os, json
import matplotlib.pyplot as plt
from collections import defaultdict
from statistics import median

# get path relative to *this file*, not relative to user's current directory
def relpath (file):
    basedir = os.getcwd()
    scriptpath = __file__
    return os.path.abspath(os.path.join(basedir, scriptpath, '../', file))

with open(relpath('data/posts_parsed.json'), 'r') as f:
    posts = json.load(f)

counts = [(post['link_flair_text'], post['score'], post['upvote_ratio']) for post in posts]

# group by genre, keep [upvote, downvote] tuples per post
d = defaultdict(list)
for genre, score, upvote_ratio in counts:
    upvotes   = score * upvote_ratio / (2 * upvote_ratio - 1)
    downvotes = upvotes - score
    d[genre].append((round(upvotes), round(downvotes), score, upvote_ratio))

# let u = # upvotes
# let d = # downvotes
# let s = post score
# let r = upvote_ratio
#
#  then
#               u - d = s                   (by definition)
#  or           u     = s + d
#  so           u - s =     d               (eq. 1)
#
#  and
#                   r = u / (u + d)         (by definition)
#  or               r = u / (u + (u - s))   (sub eq. 1)
#  or               r = u / (2u - s)
#  or    (2u - s) * r = u
#  or        2ur - sr = u
#  or             -sr = u - 2ur = u * (1 - 2r)
#  so  -sr / (1 - 2r) = u = sr / (2r - 1)

# uncomment to verify the above
#for (genre, posts) in list(d.items()):
#    for post in posts:
#        (upvotes, downvotes, score, upvote_ratio) = post
#        print(f'{upvote_ratio:1.2f}',"=",f'{round(upvotes/(upvotes+downvotes),2):1.2f}',"::",post)

# find median # upvotes / downvotes per genre
tuples = []
for (genre, posts) in list(d.items()):
    upvotes, downvotes, score, upvote_ratio = zip(*posts)
    tuples.append((genre, median(upvotes), -1*median(downvotes)))

tuples = sorted(tuples, key=lambda x: x[1])
genres, upvotes, downvotes = zip(*tuples)

plt.bar(genres, downvotes, label="Median Downvotes")
plt.bar(genres, upvotes,   label="Median Upvotes")

plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()

plt.savefig(relpath('plots/upvotes_downvotes_by_genre.png'), dpi=100)
#plt.show()
