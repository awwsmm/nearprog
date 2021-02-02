import os, json
import matplotlib.pyplot as plt
from collections import Counter

# get path relative to *this file*, not relative to user's current directory
def relpath (file):
    basedir = os.getcwd()
    scriptpath = __file__
    return os.path.abspath(os.path.join(basedir, scriptpath, '../', file))

with open(relpath('data/traffic.json'), 'r') as f:
    traffic = json.load(f)

hour = traffic["hour"]
  
print(hour)