"""INJECTED flakiness: ordering assumptions."""
import queue, random, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_first_set_element_is_alpha():
    assert list({"alpha", "beta", "gamma"})[0] == "alpha"

def test_dict_keys_from_set_in_order():
    assert list(dict.fromkeys({"north", "south"})) == ["north", "south"]

def test_futures_complete_in_submit_order():
    def work(i):
        time.sleep(random.uniform(0, 0.02))
        return i
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(work, i) for i in range(2)]
        done = [f.result() for f in as_completed(futures)]
    assert done == [0, 1]

def test_consumer_receives_items_in_order():
    q = queue.Queue()
    def producer(i):
        time.sleep(random.uniform(0, 0.02))
        q.put(i)
    threads = [threading.Thread(target=producer, args=(i,)) for i in range(2)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert [q.get(), q.get()] == [0, 1]
