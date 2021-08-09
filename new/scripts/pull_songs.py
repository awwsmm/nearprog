import sys
sys.path.extend(['..', '../src/modules'])

from src.pull import Pull
from src.modules.core.timestamp import Timestamp, day

print(", ".join(map(lambda s: s.as_JSON(), Pull.songs(Timestamp.now() - 3*day))))