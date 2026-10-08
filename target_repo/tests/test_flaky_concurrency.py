"""INJECTED flakiness: concurrency."""
import random, threading, time

def test_unsynchronised_counter():
    counter = {"n": 0}
    def bump():
        v = counter["n"]
        time.sleep(random.uniform(0, 0.002))
        counter["n"] = v + 1
    t1 = threading.Thread(target=bump); t1.start()
    time.sleep(random.uniform(0, 0.004))
    t2 = threading.Thread(target=bump); t2.start()
    t1.join(); t2.join()
    assert counter["n"] == 2

def test_lazy_init_runs_once():
    calls, state = [], {"ready": False}
    def init():
        if not state["ready"]:
            time.sleep(random.uniform(0, 0.01))
            calls.append(1)
            state["ready"] = True
    t1 = threading.Thread(target=init); t1.start()
    time.sleep(random.uniform(0, 0.01))
    t2 = threading.Thread(target=init); t2.start()
    t1.join(); t2.join()
    assert len(calls) == 1
