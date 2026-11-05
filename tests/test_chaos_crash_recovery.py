"""Kill the relay mid-batch and assert no loss and no duplicate delivery.

This is the test behind outboxed's core guarantee: once a transaction
commits, its event is delivered at least once and is observed exactly once
by the backend's handler (the dedup layer filters transport-level repeats).
"""

import random

from sqlalchemy import create_engine

from outboxed.backends.in_memory import InMemoryBackend
from outboxed.dedup import DeliveryTracker
from outboxed.models import Event, metadata
from outboxed.outbox import Outbox
from outboxed.relay import Relay


def make_engine():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


def test_crash_mid_batch_then_restart_delivers_everything_once(monkeypatch):
    engine = make_engine()
    outbox = Outbox()
    backend = InMemoryBackend()
    tracker = DeliveryTracker()

    event_count = 20
    with engine.begin() as conn:
        for i in range(event_count):
            outbox.enqueue(conn, Event(topic="orders", payload=str(i)))

    crash_after = random.randint(1, event_count - 1)
    publish_calls = {"count": 0}
    real_publish = backend.publish

    def flaky_publish(**kwargs):
        if publish_calls["count"] == crash_after:
            raise RuntimeError("simulated crash mid-batch")
        publish_calls["count"] += 1
        real_publish(**kwargs)

    monkeypatch.setattr(backend, "publish", flaky_publish)

    relay = Relay(engine, backend, batch_size=1, tracker=tracker)
    for _ in range(event_count):
        try:
            relay.poll_once()
        except RuntimeError:
            monkeypatch.setattr(backend, "publish", real_publish)

    relay.poll_once()

    delivered_payloads = [m.payload for m in backend.messages]
    assert sorted(delivered_payloads, key=int) == [str(i) for i in range(event_count)]
    assert len(delivered_payloads) == len(set(delivered_payloads))
