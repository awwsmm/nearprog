#import datetime
#import re # regular expressions
#import json

import parent # import parent directory scripts
import nearprog  # ...which includes this

# Usage:
#  1) fetch all data to a temporary file by setting fetch = True and running $ python3 pull_data.py
#  2) parse all data in the raw.txt file by setting fetch = False and running $ python3 pull_data.py

#fetch = False
#limit = None

data = nearprog.get()
traffic = data.traffic()

print(traffic)