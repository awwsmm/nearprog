from timestamp import Timestamp

def test_now():
    """Test that Timestamp.now() returns some reasonable number."""

    assert Timestamp.now() > 1628000000
