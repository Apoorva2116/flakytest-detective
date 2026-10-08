"""Simulated external services + shared state.
Nondeterminism lives HERE, so several tests look innocent when you read only the test body."""
import random, time

CACHE = {}
CONFIG = {"timeout": 30}
LOG = []

def fetch_status():
    return 503 if random.random() < 0.15 else 200

def fetch_price(item):
    if random.random() < 0.12:
        raise ConnectionError("connection reset by peer")
    return {"pen": 10, "book": 250}.get(item, 1)

def lookup_user(uid):
    return None if random.random() < 0.10 else {"id": uid, "name": f"user{uid}"}

def resolve_host(host):
    if random.random() < 0.08:
        raise TimeoutError(f"DNS lookup for {host} timed out")
    return "10.0.0." + str(len(host) % 250)

def slow_call():
    time.sleep(random.uniform(0, 0.04))
    return "ok"

class ConnectionPool:
    CAPACITY = 3
    def __init__(self):
        self.in_use = random.randint(0, 4)      # other jobs share the pool
    def acquire(self):
        if self.in_use >= self.CAPACITY:
            return False
        self.in_use += 1
        return True

def can_open_file():
    return random.randint(0, 99) > 8            # descriptor limit sometimes reached
