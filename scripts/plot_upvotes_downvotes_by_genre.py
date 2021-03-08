import os, json, pathlib, sys
from collections import defaultdict
from statistics import median
import plotly.graph_objects as go

basedir = pathlib.Path(__file__).parent

#===============================================================================
#
#  create a stacked bar chart showing median post up/downvotes by genre
#
#-------------------------------------------------------------------------------
#
#  run with
#    $ python3 path/to/plot_upvotes_downvotes_by_genre.py [save]
#
#-------------------------------------------------------------------------------

def plot_upvotes_downvotes_by_genre(export = False):

    with (basedir / 'data/posts_parsed.json').open('r') as f:
        posts = json.load(f)

    counts = [(post['link_flair_text'], post['score'], post['upvote_ratio']) for post in posts if post['author'] != "None"]

    # group by genre, keep [upvote, downvote] tuples per post
    d = defaultdict(list)
    for genre, score, upvote_ratio in counts:
        if (score != 0):
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

    #  edge case
    #    when u == d, s == 0 and r == 1/2
    #    it's not possible to determine u or d, so skip

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

    fig = go.Figure()
    fig.add_trace(go.Bar(x=genres, y=downvotes, name="Median Downvotes per Post"))
    fig.add_trace(go.Bar(x=genres, y=upvotes, name="Median Upvotes per Post"))

    fig.update_layout(
        barmode="relative",
        title_text="Median Upvotes / Downvotes by Genre",
        width=1000,
        height=600,
        legend=dict(
            x=0.05,
            y=0.95,
            traceorder="reversed"
        )
    )

    if (export):
        fig.write_image(str(basedir / f'plots/upvotes_downvotes_by_genre.svg')) # pip3 install kaleido
    else:
        fig.show()

# command-line testing
if ("plot_upvotes_downvotes_by_genre.py" in sys.argv[0]):
    if (len(sys.argv) > 1 and sys.argv[1] == "save"):
        plot_upvotes_downvotes_by_genre(export=True)
    else:
        plot_upvotes_downvotes_by_genre()