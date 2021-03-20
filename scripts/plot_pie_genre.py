import sys, json, pathlib, argparse
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
#    $ python3 path/to/plot_pie_genre.py [-h]
#
#-------------------------------------------------------------------------------

def pie_genre(optUser = "", rotation = 295, export = False):

    with (basedir / 'data/posts_parsed.json').open('r') as f:
        posts = json.load(f)

    if (optUser == ""):
        plot_title_text="r/nearprog Top Genres"
        counts = Counter([post['link_flair_text'] for post in posts])
        file_name = "pie_genre.png"
    else:
        if (optUser.startswith("u/")):
            username = optUser[2:] # remove "u/" if present
        else:
            username = optUser
        plot_title_text=f"u/{username} Top Genres"
        counts = Counter([post['link_flair_text'] for post in posts if post['author'] == username])
        file_name = f"pie_genre_for_{username}.png"

    ordered = counts.most_common()
    keys, values = zip(*ordered)

    # Pie chart
    fig = go.Figure(data=[
        go.Pie(
            labels = keys,
            values = values,
            textinfo = 'label+percent',
            insidetextorientation = 'horizontal',
            rotation=rotation
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

    # TODO add "plot saved to /path/to/plot" message upon save
    if (export):
        fig.write_image(str(basedir / f'plots/{file_name}')) # pip3 install kaleido
    else:
        fig.show()

# command-line testing
if ("plot_pie_genre.py" in sys.argv[0]):

    desc = "Script to plot subreddit-wide or user-specific genre flair pie chart."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-u", dest="username", metavar="u/sername", type=str, default="",
        help="username including leading 'u/' (ex. \"u/_awwsmm\")")

    parser.add_argument('-r', dest="degrees", type=int, default=295,
        help="integer number of degrees to [r]otate pie chart slices [0, 360): default 295")

    parser.add_argument('-s', dest="save", action='store_true',
        help="[s]ave the plot to a PNG file")

    args = parser.parse_args()
    pie_genre(args.username, args.degrees, args.save)