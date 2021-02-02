import json, pathlib
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

basedir = pathlib.Path(__file__).parent

#===============================================================================

with (basedir / 'data/traffic_newest.json').open('r') as f:
    traffic = json.load(f)

hour = traffic["day"]
timestamps, unique_pageviews, total_pageviews, users = zip(*hour)

# convert UNIX timestamps to datetime objects
datetimes = list(map(lambda x: datetime.utcfromtimestamp(x), timestamps))

print(datetimes)
print(unique_pageviews)
print(total_pageviews)
print(users)