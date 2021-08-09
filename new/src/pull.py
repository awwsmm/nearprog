from pathlib import Path
from typing import Iterator

from src.modules.core.config import Config
from src.modules.core.submission import Submission
from src.modules.connection import Connection

class Pull:

    @staticmethod
    def songs(since: int):
        """Pulls all song submissions from r/nearprog since the given UTC UNIX timestamp."""

        path = Path(__file__).parent
        to = '../resources/'
        file = 'config.json'

        # connect to r/nearprog and fetch recent song submissions
        config = Config.read((path / to / file).resolve())
        connection = Connection(config)
        submissions: Iterator[Submission] = connection.fetch_submissions(since = since)
        songs = filter(lambda s: s.is_song(), submissions)

        # sort old-to-new by timestamp (use timestamp as primary key)
        return sorted(songs, key = lambda s: s.timestamp)
