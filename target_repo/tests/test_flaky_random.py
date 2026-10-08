"""INJECTED flakiness: random values (visible in the test)."""
import random

def test_shuffle_keeps_first_item_small():
    items = [1, 2, 3, 4]
    random.shuffle(items)
    assert items[0] != 4

def test_sample_never_contains_five():
    assert 5 not in random.sample(range(10), 3)

def test_gaussian_within_two_sigma():
    assert abs(random.gauss(0, 1)) < 2

def test_coin_flips_not_all_heads():
    flips = [random.random() < 0.5 for _ in range(3)]
    assert not all(flips)
