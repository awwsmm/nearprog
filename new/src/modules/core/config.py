import json
from pathlib import Path

class Config:
    """Information required to connect to Reddit via PRAW.

    See: https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example
    And: https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html
    And: https://www.reddit.com/prefs/apps
    """

    def __init__(self, client_id: str, client_secret: str, username: str, password: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
    
    @staticmethod
    def parse(JSON: str) -> None:
        """Read the required configuration information from a JSON-formatted string."""

        try:
            data = json.loads(JSON)
            client_id = data['client_id']
            client_secret = data['client_secret']
            username = data['username']
            password = data['password']

            return Config(client_id, client_secret, username, password)

        except:
            raise ValueError('Cannot parse provided string as Config.')

    @staticmethod
    def read(path: Path) -> None:
        """Read the required configuration information from a file."""

        with path.open('r') as f:
            data = f.read()
            return Config.parse(data)
