from pathlib import Path
import pytest
import random
from typing import Iterator

from connection import Connection
from core.config import Config
from core.submission import Submission, Fetcher
from core.timestamp import Timestamp, week, hour, day

def get_config() -> Config:
    """Some tests in this suite connect to Reddit, and so require a valid config.json file."""

    path = Path(__file__).parent
    to = '../../resources/'
    file = 'config.json'

    try:
        config_file: Path = (path / to / file).resolve()
        return Config.read(config_file)

    except:
        raise FileNotFoundError(f'{config_file} not found. Cannot run all Connection tests.')

def test_connection_good():
    """Test that Connection.reddit() successfully connects when provided with valid Config."""

    config = get_config()
    connection: Connection = Connection(config)
    assert connection.reddit().username_available('_awwsmm') == False

def test_unauthorized_user():
    """Test that Connection.reddit() fails when provided with valid client -- but invalid user -- Config."""

    config = get_config()
    bad_username = 'awwsmm'
    bad_config: Config = Config(config.client_id, config.client_secret, bad_username, config.password)
    connection: Connection = Connection(bad_config)

    with pytest.raises(PermissionError) as excinfo:
        connection.reddit()
    assert f'User "{bad_username}" is not authorized to use this app.' in str(excinfo.value)

def test_invalid_client():
    """Test that Connection.reddit() fails when provided with invalid client Config."""

    JSON = """
    {
        "client_id":     "not_my_client_id",
        "client_secret": "not_my_client_secret",
        "username":      "_awwsmm",
        "password":      "not_my_password"
    }
    """

    config: Config = Config.parse(JSON)
    connection: Connection = Connection(config)

    with pytest.raises(ConnectionRefusedError) as excinfo:
        connection.reddit()
    assert 'Connection authentication error. Check Config.' in str(excinfo.value)

def test_fetch_submissions_count():
    """Test that Connection.fetch_submissions() returns the correct number of submissions."""

    config = get_config()
    connection: Connection = Connection(config)

    limit: int = 5

    # remove 'fetcher' argument to test this method directly with Reddit
    submissions = connection.fetch_submissions(fetcher = Fetcher(Fixture.fetcher), since = 0, limit = limit)

    assert len(submissions) == limit

def test_fetch_submissions_age():
    """Test that Connection.fetch_submissions() returns the oldest-available submissions."""

    config = get_config()
    connection: Connection = Connection(config)

    # remove 'fetcher' argument to test this method directly with Reddit
    old = connection.fetch_submissions(fetcher = Fetcher(Fixture.fetcher), since = 0, limit = 1)
    new = connection.fetch_submissions(fetcher = Fetcher(Fixture.fetcher), since = Timestamp.now() - week, limit = 1)

    assert old[0].timestamp < new[0].timestamp

def test_fetch_submissions_since():
    """Test that Connection.fetch_submissions() only returns submissions since the given UTC UNIX timestamp."""

    config = get_config()
    connection: Connection = Connection(config)

    # remove 'fetcher' argument to test this method directly with Reddit
    since = Timestamp.now() - 24*hour
    submissions = connection.fetch_submissions(fetcher = Fetcher(Fixture.fetcher), since = since)

    assert submissions[0].timestamp >= since

def test_fetch_submissions_ordering():
    """Test that Connection.fetch_submissions() returns the Submissions sorted oldest -> newest."""

    config = get_config()
    connection: Connection = Connection(config)

    # remove 'fetcher' argument to test this method directly with Reddit
    since = Timestamp.now() - 30*day
    submissions = connection.fetch_submissions(fetcher = Fetcher(Fixture.fetcher), since = since)

    assert submissions[0].timestamp < submissions[1].timestamp
    assert submissions[1].timestamp < submissions[2].timestamp

class Fixture:

    @staticmethod
    def fetcher(limit: int) -> Iterator[Submission]:
        # assume 1 submission every ~6 hours on average
        end_time = int(Timestamp.now())
        start_time = int(end_time - limit * 6*hour)
        timestamps = sorted(random.sample(range(start_time, end_time), limit))
        return iter(Submission(timestamp) for timestamp in timestamps)
