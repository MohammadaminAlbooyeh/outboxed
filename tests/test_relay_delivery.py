"""Polling, ordering, and marking entries delivered."""

from sqlalchemy import create_engine

from outboxed.backends.in_memory import InMemoryBackend
from outboxed.models import Event, metadata
from outboxed.outbox import Outbox
from outboxed.relay import Relay


def make_engine():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


def test_poll_once_delivers_in_order():
    engine = make_engine()
    outbox = Outbox()
    backend = InMemoryBackend()
    relay = Relay(engine, backend)

    with engine.begin() as conn:
        outbox.enqueue(conn, Event(topic="orders", payload="1"))
        outbox.enqueue(conn, Event(topic="orders", payload="2"))

    delivered = relay.poll_once()

    assert delivered == 2
    assert [m.payload for m in backend.messages] == ["1", "2"]


def test_poll_once_skips_already_delivered_entries():
    engine = make_engine()
    outbox = Outbox()
    backend = InMemoryBackend()
    relay = Relay(engine, backend)

    with engine.begin() as conn:
        outbox.enqueue(conn, Event(topic="orders", payload="1"))

    relay.poll_once()
    delivered_again = relay.poll_once()

    assert delivered_again == 0
    assert len(backend.messages) == 1
