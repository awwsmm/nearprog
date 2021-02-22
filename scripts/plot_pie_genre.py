import sys, json, pathlib
import plotly.graph_objects as go
from collections import Counter

basedir = pathlib.Path(__file__).parent

#===============================================================================
#
#  create a pie chart of most-used genre flairs
#
#-------------------------------------------------------------------------------
#
#  run with
#    $ python3 path/to/plot_pie_genre.py [u/UserName] [save]
#
#-------------------------------------------------------------------------------

def pie_genre(optUser = "", export = False):

    with (basedir / 'data/posts_parsed.json').open('r') as f:
        posts = json.load(f)

    if (optUser == ""):
        plot_title_text="r/nearprog Top Genres"
        counts = Counter([post['link_flair_text'] for post in posts])
        file_name = "pie_genre.svg"
    else:
        if (optUser.startswith("u/")):
            username = optUser[2:] # remove "u/" if present
        else:
            username = optUser
        plot_title_text=f"u/{username} Top Genres"
        counts = Counter([post['link_flair_text'] for post in posts if post['author'] == username])
        file_name = f"pie_genre_for_{username}.svg"

    ordered = counts.most_common()
    keys, values = zip(*ordered)

    # Pie chart
    fig = go.Figure(data=[
        go.Pie(
            labels = keys,
            values = values,
            textinfo = 'label+percent',
            insidetextorientation = 'horizontal',
            rotation=-65
        )])

    # Use `hole` to create a donut-like pie chart
    fig.update_traces(
        hole = 0.4,
        hoverinfo="label+percent+value",
        textposition='outside'
        )

    fig.update_layout(
        title_text=plot_title_text,
        # Add annotations in the center of the donut pies.
        # annotations=[dict(text='', x=0.18, y=0.5, font_size=20, showarrow=False)],
        autosize=False,
        width=800,
        height=800,
        showlegend=False,
        # legend=dict(
        #     orientation="h",
        #     yanchor="bottom",
        #     y=-0.5,
        #     xanchor="left",
        #     x=0
        # ),
        margin=dict(
            l=0,
            r=0,
            b=50,
            t=300,
            pad=0
        ),
        paper_bgcolor="LightSteelBlue"
    )

    if (export):
        fig.write_image(str(basedir / f'plots/{file_name}')) # pip3 install kaleido
    else:
        fig.show()

# command-line testing
if ("plot_pie_genre.py" in sys.argv[0]):

    # user-specific
    if (len(sys.argv) > 1 and sys.argv[1].startswith("u/")):
        if (len(sys.argv) > 2 and sys.argv[2] == "save"):
            pie_genre(sys.argv[1], True)
        else:
            pie_genre(sys.argv[1])

    # for entire subreddit
    else:
        if (len(sys.argv) > 1 and sys.argv[1] == "save"):
            pie_genre(export=True)
        else:
            pie_genre()