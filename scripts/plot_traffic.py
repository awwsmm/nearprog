import json, pathlib, sys, argparse
from datetime import datetime
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from copy import deepcopy
from datetime import timedelta

basedir = pathlib.Path(__file__).parent

#===============================================================================
#
#  create a line chart of traffic at a monthly, daily, or hourly frequency
#
#-------------------------------------------------------------------------------
#
#  run with
#    $ python3 path/to/plot_traffic.py [-h]
#
#-------------------------------------------------------------------------------

def plot_traffic(view = "all", export = False):

    with (basedir / 'data/traffic_merged.json').open('r') as f:
        traffic = json.load(f)

    with (basedir / 'data/promotion_posts.json').open('r') as f:
        promos = json.load(f)

    # # sort promos by score and then by upvote ratio
    # promos = sorted(promos, key = lambda x: (int(x["score"]), float(x["upvote_ratio"])), reverse = True)

    # sort promos in reverse order by timestamp
    promos = sorted(promos, key = lambda x: float(x["created_utc"]), reverse = True)

    # here, we use daily data
    if (view == "all"):
        # drop the first day (today) because there's incomplete data
        # ...also drop the last 16 days, because that's before the sub began
        timestamps, unique_pageviews, total_pageviews, users = zip(*traffic["day"][1:-16])
        total_users = list(reversed(np.cumsum(list(reversed(users)))))
        
        # convert UNIX timestamps to datetime objects
        datetimes = list(map(lambda x: datetime.utcfromtimestamp(x), timestamps))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=datetimes, y=unique_pageviews, name='Unique Pageviews'))

        # fig.add_trace(go.Scatter(x=datetimes, y=total_pageviews, name='Total Pageviews'))
        fig.add_trace(go.Scatter(x=datetimes, y=users, name='New Users')) #, mode='lines+markers'))
        fig.add_trace(go.Scatter(x=datetimes, y=total_users, name='Total Users')) #, mode='lines+markers'))

        # add some padding in the plot
        fig.update_xaxes(range=[datetimes[-1]-timedelta(days=30),datetimes[0]+timedelta(days=30)])

        ypos = 1500
        ydelta = -120
        ysteps = 0

        for p in promos:
            if (int(p["score"]) > 26 and float(p["upvote_ratio"]) > 0.95):
                utc_timestamp = float(p["created_utc"])
                # actual_time_posted = datetime.utcfromtimestamp(utc_timestamp)
                rounded_timestamp = utc_timestamp - (utc_timestamp % (24 * 60 * 60))
                rounded_time_posted = datetime.utcfromtimestamp(rounded_timestamp)

                fig.add_annotation(x=rounded_time_posted, y=ypos+ydelta*ysteps,
                    text=p["title"],
                    # text="&nbsp;"*15*max(0, ysteps-7)+p["title"]+"&nbsp;"*15*max(0, 7-ysteps),
                    # showarrow=True,
                    # arrowhead=1
                    )

                index = timestamps.index(rounded_timestamp)
                ymax = max(unique_pageviews[index], total_users[index])

                fig.add_shape(type="line",
                    x0=rounded_time_posted, x1=rounded_time_posted,
                    y0=0, y1=ymax,
                    line=dict(color="#999999",width=1,dash="dot")
                )

                ysteps += 1

        fig.update_layout(title_text="r/nearprog Growth Over Time<br><span style='font-size:9pt;color:#666'>with high-impact (27+ upvotes, 95%+ upvote ratio) crossposts and promotions highlighted</span>")
        fig.update_layout(width=1000, height=600)

        if (export):
            fig.write_image(str(basedir / f'plots/traffic_all.png')) # pip3 install kaleido
        else:
            fig.show()

    # here, we use hourly data
    # TODO simplify / deduplicate code below
    else:
        timestamps, unique_pageviews, total_pageviews = zip(*traffic["hour"])
        hours = [t / 3600 for t in timestamps]
        zero_hour = min(hours)
        
        # convert UNIX timestamps to datetime objects
        datetimes = list(map(lambda x: datetime.utcfromtimestamp(x), timestamps))

        # for hourly data, plot Unique and Total views on independent y-axes
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        if (view == "week"):
            fig.update_layout(title_text="Total / Unique Page Views (by hour of week)")
            hours_per_week = 24 * 7
            hour_of_week = [(h - zero_hour) % hours_per_week for h in hours]

            fig.add_trace(
                go.Box(x=hour_of_week, y=unique_pageviews, name='Unique Pageviews'),
                secondary_y = True)

            fig.add_trace(
                go.Box(x=hour_of_week, y=total_pageviews, name='Total Pageviews'),
                secondary_y = False)

            # TODO align ticks like https://github.com/VictorBezak/Plotly_Multi-Axes_Gridlines

            # Set titles of primary and secondary axes
            fig.update_yaxes(secondary_y = False,
                title_text="<span style='font-weight:bold;color:#d62728'>Total</span> page views")

            fig.update_yaxes(secondary_y = True, showgrid = False,
                title_text = "<span style='font-weight:bold;color:#1f77b4'>Unique</span> page views")

            fig.update_layout(width=1000, height=600)

            if (export):
                fig.write_image(str(basedir / f'plots/traffic_week.png')) # pip3 install kaleido
            else:
                fig.show()

        elif (view == "day"):
            fig.update_layout(title_text="Total / Unique Page Views (by hour of day)")
            hours_per_day = 24
            hour_of_day = [(h - zero_hour) % hours_per_day for h in hours]

            fig.add_trace(
                go.Box(x=hour_of_day, y=unique_pageviews, name='Unique Pageviews'),
                secondary_y = True)

            fig.add_trace(
                go.Box(x=hour_of_day, y=total_pageviews, name='Total Pageviews'),
                secondary_y = False)

            # TODO align ticks like https://github.com/VictorBezak/Plotly_Multi-Axes_Gridlines

            # Set titles of primary and secondary axes
            fig.update_yaxes(secondary_y = False,
                title_text="<span style='font-weight:bold;color:#d62728'>Total</span> page views")

            fig.update_yaxes(secondary_y = True, showgrid = False,
                title_text = "<span style='font-weight:bold;color:#1f77b4'>Unique</span> page views")

            fig.update_layout(width=1000, height=600)

            if (export):
                fig.write_image(str(basedir / f'plots/traffic_day.png')) # pip3 install kaleido
            else:
                fig.show()

        else:
            print(f"ERROR: Unknown data view '{view}'. Please choose 'week', 'day', or 'all'.")
            sys.exit(1)

# command-line testing
if ("plot_traffic.py" in sys.argv[0]):

    desc = "Script to plot traffic data per day or week, or overall with key promotion events."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-f", dest="fold", type=str, default="all", choices=['week', 'day'],
        help="[f]old the data, either onto one \"week\" or one \"day\"")

    parser.add_argument('-s', dest="save", action='store_true',
        help="[s]ave the plot to a PNG file")

    args = parser.parse_args()
    plot_traffic(args.fold, args.save)