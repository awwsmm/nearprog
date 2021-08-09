from pathlib import Path
import pytest

from config import Config

def test_parse_good():
    """Test that Config.parse() parses correctly-JSON-formatted string config info."""

    JSON = """
    {
        "client_id":     "my_client_id",
        "client_secret": "my_client_secret",
        "username":      "my_username",
        "password":      "my_password"
    }
    """

    config: Config = Config.parse(JSON)

    assert config.client_id == 'my_client_id'
    assert config.client_secret == 'my_client_secret'
    assert config.username == 'my_username'
    assert config.password == 'my_password'

def test_parse_bad():
    """Test that Config.parse() raises a ValueError when it cannot parse the given string."""

    JSON = """
    {
        "client_id":     "my_client_id",
        "client_secret": "this JSON file is missing a key: username",
        "password":      "my_password"
    }
    """

    with pytest.raises(ValueError) as excinfo:
        config: Config = Config.parse(JSON)
    assert 'Cannot parse provided string as Config.' in str(excinfo.value)

    NOT_JSON = "This is not JSON."

    with pytest.raises(ValueError) as excinfo:
        config: Config = Config.parse(NOT_JSON)
    assert 'Cannot parse provided string as Config.' in str(excinfo.value)

def test_read():
    """Test that Config.read() correctly reads config info from an external file."""

    path = Path(__file__).parent
    to = '../../../resources/'
    file = 'test_config.json'
    
    config: Config = Config.read((path / to / file).resolve())

    assert config.client_id == 'my_client_id'
    assert config.client_secret == 'my_client_secret'
    assert config.username == 'my_username'
    assert config.password == 'my_password'
