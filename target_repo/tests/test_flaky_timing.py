"""INJECTED flakiness: timing and deadlines."""
import random, threading, time
import services

def test_response_within_deadline():
    start = time.perf_counter()
    time.sleep(random.uniform(0, 0.03))
    assert time.perf_counter() - start < 0.02

def test_slow_call_finishes_in_budget():
    start = time.perf_counter()
    assert services.slow_call() == "ok"
    assert time.perf_counter() - start < 0.03

def test_event_set_before_timeout():
    ev = threading.Event()
    threading.Timer(random.uniform(0, 0.04), ev.set).start()
    assert ev.wait(timeout=0.025)
