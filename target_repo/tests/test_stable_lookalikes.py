"""STABLE tests that LOOK suspicious (random, threads, sleep, uuid, time) but are deterministic.
They exist to test for false alarms."""
import hashlib, queue, random, tempfile, threading, time, uuid
from datetime import date, datetime, timedelta

def test_seeded_random_repeatable():
    r1, r2 = random.Random(7), random.Random(7)
    assert [r1.random() for _ in range(3)] == [r2.random() for _ in range(3)]

def test_seeded_shuffle_repeatable():
    a, b = list(range(6)), list(range(6))
    random.Random(3).shuffle(a); random.Random(3).shuffle(b)
    assert a == b

def test_seeded_choice_in_range():
    assert random.Random(1).choice([1, 2, 3]) in [1, 2, 3]

def test_thread_joined_before_assert():
    flag = {"done": False}
    def worker():
        time.sleep(0.01)
        flag["done"] = True
    t = threading.Thread(target=worker); t.start(); t.join()
    assert flag["done"]

def test_thread_results_after_join():
    out = []
    ts = [threading.Thread(target=out.append, args=(i,)) for i in range(3)]
    for t in ts: t.start()
    for t in ts: t.join()
    assert sorted(out) == [0, 1, 2]

def test_lock_protected_counter():
    lock, c = threading.Lock(), {"n": 0}
    def bump():
        for _ in range(50):
            with lock: c["n"] += 1
    ts = [threading.Thread(target=bump) for _ in range(4)]
    for t in ts: t.start()
    for t in ts: t.join()
    assert c["n"] == 200

def test_queue_drained_fully():
    q = queue.Queue()
    for i in range(5): q.put(i)
    assert sorted(q.get() for _ in range(5)) == [0, 1, 2, 3, 4]

def test_sorted_set_order(): assert sorted({"b", "a", "c"}) == ["a", "b", "c"]
def test_set_equality_ignores_order(): assert {"x", "y"} == {"y", "x"}

def test_uuid_format():
    u = uuid.uuid4()
    assert len(str(u)) == 36 and u.version == 4

def test_uuid_pair_differs(): assert uuid.uuid4() != uuid.uuid4()

def test_uuid5_deterministic():
    assert uuid.uuid5(uuid.NAMESPACE_DNS, "example.com") == uuid.uuid5(uuid.NAMESPACE_DNS, "example.com")

def test_fixed_date_add_days():
    assert datetime(2024, 1, 30) + timedelta(days=3) == datetime(2024, 2, 2)

def test_fixed_date_weekday(): assert date(2024, 1, 1).weekday() == 0

def test_sleep_lower_bound():
    start = time.perf_counter(); time.sleep(0.01)
    assert time.perf_counter() - start >= 0.005

def test_md5_known_value():
    assert hashlib.md5(b"abc").hexdigest() == "900150983cd24fb0d6963f7d28e17f72"

def test_dict_insertion_order(): assert list({"a": 1, "b": 2}) == ["a", "b"]

def test_tempfile_roundtrip():
    with tempfile.TemporaryFile("w+") as f:
        f.write("hello"); f.seek(0)
        assert f.read() == "hello"
