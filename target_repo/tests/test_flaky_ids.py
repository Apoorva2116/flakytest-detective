"""INJECTED flakiness: random IDs and tokens."""
import random, secrets, uuid

def test_uuid_starts_with_letter():
    assert str(uuid.uuid4())[0].isalpha()

def test_random_ids_are_distinct():
    ids = [random.randint(1, 30) for _ in range(8)]
    assert len(set(ids)) == len(ids)

def test_token_has_no_repeated_ff():
    assert "ff" not in secrets.token_hex(8)
