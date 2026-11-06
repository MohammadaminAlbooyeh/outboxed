# Quickstart

## Install

```bash
pip install outboxed
pip install "outboxed[kafka]"   # or [redis], [sqs] — pick the backend you need
```

## 1. Create the outbox table

`outboxed` ships its table definition as SQLAlchemy metadata, so it can live
in the same database as your application's own tables.

```python
from sqlalchemy import create_engine
from outboxed.models import metadata

engine = create_engine("postgresql://...")
metadata.create_all(engine)
```

In a project with its own migrations (Alembic, etc.), import
`outboxed.models.outbox_table` and let your migration tool manage it instead
of calling `create_all`.

## 2. Enqueue events in your business transaction

```python
from outboxed import Outbox, Event

outbox = Outbox()

with engine.begin() as conn:
    conn.execute(orders_table.insert().values(id=1, status="placed"))
    outbox.enqueue(conn, Event(topic="orders", key="1", payload='{"id": 1}'))
    # both inserts commit together, or neither does
```

## 3. Run a relay to deliver them

Pick a backend and run the relay as its own process (a long-running worker,
not inside your web server):

```python
from outboxed import Relay
from outboxed.backends.redis_streams import RedisStreamsBackend
import redis

backend = RedisStreamsBackend(redis.Redis())
relay = Relay(engine, backend=backend)
relay.run_forever()
```

For a one-off batch (e.g. inside a cron job or test), call
`relay.poll_once()` instead — it processes one batch and returns the number
of rows delivered.

## Next steps

- [docs/dual-write-problem.md](dual-write-problem.md) — why this pattern exists.
- [docs/guarantees.md](guarantees.md) — exact delivery semantics.
- [docs/backends.md](backends.md) — writing your own backend.
