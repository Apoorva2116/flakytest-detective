"""INJECTED flakiness: timestamps / wall clock."""
import time
from datetime import datetime

def test_clock_second_is_even():
    assert int(time.time()) % 2 == 0

def test_second_not_multiple_of_ten():
    assert datetime.now().second % 10 != 0

def test_millis_not_multiple_of_five():
    assert int(time.time() * 1000) % 5 != 0
