"""Shared-state pollution. Each 'writer' test passes on its own; the 'reader' that runs after it
fails only when the writer happened to pollute the state."""
import random
import services

def test_warm_cache_helper():
    if random.random() < 0.3:
        services.CACHE["session"] = "stale"
    assert isinstance(services.CACHE, dict)

def test_cache_starts_empty():
    assert "session" not in services.CACHE

def test_audit_log_writer():
    if random.random() < 0.4:
        services.LOG.append("login")
    assert isinstance(services.LOG, list)

def test_audit_log_is_empty():
    assert services.LOG == []

def test_override_timeout_for_debug():
    if random.random() < 0.25:
        services.CONFIG["timeout"] = 1
    assert services.CONFIG["timeout"] in (1, 30)

def test_default_timeout_is_thirty():
    assert services.CONFIG["timeout"] == 30
