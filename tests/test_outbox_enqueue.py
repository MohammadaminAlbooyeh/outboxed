"""Same-transaction write semantics: commit keeps the event, rollback drops it."""

from sqlalchemy import create_engine, select

from outboxed.models import Event, metadata, outbox_table
from outboxed.outbox import Outbox


def make_engine():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


def test_enqueue_is_visible_after_commit():
    engine = make_engine()
    outbox = Outbox()
    event = Event(topic="orders", payload='{"id": 1}')

    with engine.begin() as conn:
        outbox.enqueue(conn, event)

    with engine.connect() as conn:
        rows = conn.execute(select(outbox_table)).fetchall()

    assert len(rows) == 1
    assert rows[0].id == event.id
    assert rows[0].delivered_at is None


def test_enqueue_is_rolled_back_with_the_transaction():
    engine = make_engine()
    outbox = Outbox()
    event = Event(topic="orders", payload='{"id": 1}')

    with engine.connect() as conn:
        trans = conn.begin()
        outbox.enqueue(conn, event)
        trans.rollback()

    with engine.connect() as conn:
        rows = conn.execute(select(outbox_table)).fetchall()

    assert rows == []
