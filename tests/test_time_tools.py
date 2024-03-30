from pathlib import Path
import sys
import time

import pytest

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from utils.time_tools import get_timestamp  # noqa: E402

def test_get_timestamp_without_argument():
    """Test that get_timestamp returns an integer timestamp when no argument is passed."""
    result = get_timestamp()
    current_time = int(time.time() * 10000000)
    
    # The result should be a timestamp close to the current time
    assert isinstance(result, int)
    # Allowing a small margin for the time that has passed since the function call
    assert abs(result - current_time) < 10000000

def test_get_timestamp_with_argument():
    """Test that get_timestamp converts a provided float time correctly."""
    test_time = 1672525600.123  # This represents a specific date and time
    expected_timestamp = int(test_time * 10000000)
    result = get_timestamp(test_time)
    
    assert result == expected_timestamp

def test_get_timestamp_with_negative_float():
    """Test that get_timestamp handles negative float values correctly."""
    test_time = -12345.678
    expected = int(test_time * 10000000)
    result = get_timestamp(test_time)
    assert result == expected, "The function should correctly convert negative float values."

def test_get_timestamp_with_large_float():
    """Test that get_timestamp handles very large float values correctly."""
    test_time = 253402300799.999  # This is the maximum datetime in Python (9999-12-31)
    expected = int(test_time * 10000000)
    result = get_timestamp(test_time)
    assert result == expected, "The function should correctly convert very large float values."

def test_get_timestamp_with_zero():
    """Test that get_timestamp handles zero correctly."""
    test_time = 0.0
    expected = 0
    result = get_timestamp(test_time)
    assert result == expected, "The function should return zero when zero is passed."

def test_get_timestamp_with_integer():
    """Test that get_timestamp handles integer values correctly."""
    test_time = 123456789
    expected = test_time * 10000000
    result = get_timestamp(test_time)
    assert result == expected, "The function should correctly convert integer values."

@pytest.mark.parametrize("invalid_value", ['string', True, [], {}])
def test_get_timestamp_with_invalid_types(invalid_value):
    """Test that get_timestamp raises an error or behaves correctly when given invalid types."""
    with pytest.raises((TypeError, ValueError)):
        get_timestamp(invalid_value)