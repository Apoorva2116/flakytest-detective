"""INJECTED flakiness. Say this clearly in the report."""
import random, threading, time, uuid
from datetime import datetime
from shop import *

def test_random_discount_applied():
    rate = 0.0 if random.random() < 0.2 else 10   # sometimes no discount
    assert discount(100, rate) == 90.0

def test_random_item_price():
    price = random.choice([10, 10, 10, 10, 10, 10, 10, 11])
    assert add(price, 5) == 15

def test_timing_budget():
    start = time.time()
    time.sleep(random.uniform(0, 0.06))
    assert time.time() - start < 0.05

def test_set_order_assumption():
    assert list({"x", "y"}) == ["x", "y"]          # depends on hash seed

def test_set_order_assumption_2():
    assert list({"red", "blue"}) == ["red", "blue"]  # depends on hash seed

def test_wall_clock_microsecond():
    assert datetime.now().microsecond < 800000

def test_uuid_first_char():
    assert str(uuid.uuid4())[0] != "a"

def test_simulated_service_timeout():
    if random.random() < 0.1:
        raise TimeoutError("upstream service timed out")
    assert total([1, 2]) == 3

def test_background_flag_race():
    flag = {"done": False}
    def worker():
        time.sleep(random.uniform(0, 0.05))
        flag["done"] = True
    threading.Thread(target=worker).start()
    time.sleep(0.03)                                 # fixed wait, no join
    assert flag["done"]

def test_timestamp_ns_modulo():
    assert time.time_ns() % 7 != 0
