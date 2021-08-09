from praw import Reddit
from praw.models import Subreddit
from prawcore.exceptions import OAuthException, PrawcoreException, ResponseException
from requests.models import Response
from typing import List, Optional

from core.config import Config
from core.submission import Submission, Fetcher
from core.timestamp import Timestamp, day

class Connection:
    """Connect to Reddit and request data via praw."""
    
    def __init__(self, config: Config) -> None:
        self.config = config

    # cache connection internally so we don't keep reconnecting
    __connection: Optional[Reddit] = None

    def reddit(self) -> Reddit:
        """Returns an instance of a connection to Reddit."""

        if (self.__connection is None):
            try:
                connection = Reddit(
                    user_agent    = "nearprog_scraper by u/_awwsmm",
                    client_id     = self.config.client_id,
                    client_secret = self.config.client_secret,
                    username      = self.config.username,
                    password      = self.config.password)

                # test the connection by sending a request
                connection.username_available('_awwsmm')

                self.__connection = connection
                return self.__connection

            except PrawcoreException as ex:

                if isinstance(ex, OAuthException):
                    response: Response = ex.response
                    raise PermissionError(f'User "{self.config.username}" is not authorized to use this app. Reason: {response.text}')

                elif isinstance(ex, ResponseException):
                    response: Response = ex.response
                    if response.status_code == 401:
                        raise ConnectionRefusedError('Connection authentication error. Check Config.')
                    else:
                        raise ValueError(f'Error connecting to Reddit. Reason: {ex.response}')

        else:
            return self.__connection
    
    def nearprog(self) -> Subreddit:
        """Returns an instance of a connection to the r/nearprog Subreddit."""

        return self.reddit().subreddit('nearprog')

    def fetch_submissions(self, fetcher: Optional[Fetcher] = None, since: int = Timestamp.now() - 10*day, limit: int = 1000) -> List[Submission]:
        """Fetches all submissions (up to 1000) since the given UTC UNIX timestamp, using the provided fetcher.
        
        If no argument is passed for 'fetcher' (or it is None), this method will request the newest posts from r/nearprog.
        """

        def fetch(extended_limit: int) -> List:

            # if None is provided, use the default (live) Submission fetcher
            default_fetcher = Fetcher(lambda n: map(lambda s: Submission.wrap(s), self.nearprog().new(limit=n)))
            submissions = list((fetcher or default_fetcher).fetch(since, extended_limit))
            earliest = min(map(lambda s: s.timestamp, submissions))

            # if we're limited only by our own self-imposed max # submissions, try again, but request more
            if (earliest > since and len(submissions) == extended_limit):
                return fetch(extended_limit * 2)
            else:
                # return the oldest submissions first (at the head of the list)
                return sorted(submissions, key = lambda x: x.timestamp)[:limit]

        return fetch(limit)
