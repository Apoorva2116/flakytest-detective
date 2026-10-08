"""INJECTED flakiness: intermittent service failures (cause hidden in services.py)."""
import services

def test_status_endpoint_returns_200():
    assert services.fetch_status() == 200

def test_price_lookup_for_book():
    assert services.fetch_price("book") == 250

def test_resolve_internal_host():
    assert services.resolve_host("db.internal").startswith("10.0.0.")

def test_user_lookup_finds_user():
    user = services.lookup_user(7)
    assert user["name"] == "user7"
