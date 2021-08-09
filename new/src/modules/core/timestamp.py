from datetime import datetime

epoch = datetime(1970, 1, 1)

# get relative times with (Timestamp.now() - 5*day), etc.
second: int = 1
minute: int = 60 * second
hour: int = 60 * minute
day: int = 24 * hour
week: int = 7 * day

class Timestamp:
    """Utility class for working with UTC UNIX timestamps as integers."""

    @staticmethod
    def now() -> float:
        """Returns the current UTC UNIX timestamp in seconds from 1970-01-01 00:00:00."""

        now = datetime.utcnow()
        return (now - epoch).total_seconds()
