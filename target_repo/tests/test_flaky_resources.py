"""INJECTED flakiness: resource availability (simulated)."""
import random
import services

def test_connection_pool_has_free_slot():
    assert services.ConnectionPool().acquire()

def test_memory_headroom_above_ten_percent():
    free_fraction = random.uniform(0, 1)
    assert free_fraction > 0.10

def test_can_open_another_file():
    assert services.can_open_file()
