# outboxed

The transactional outbox pattern for Python backends: reliably publish an
event every time — and only when — a database write actually commits.

## The problem

Writing a database row and then publishing an event about it, as two
separate steps, is the dual-write problem: a crash between them loses the
event forever, and blind retries trade that for duplicate events instead.
See [docs/dual-write-problem.md](docs/dual-write-problem.md).

## The fix

Enqueue the event as a row in an outbox table, in the same transaction as
the business write. A separate relay process polls that table and does the
actual publishing, with retries and deduplication handled on the relay
side.

```python
from sqlalchemy import create_engine
from outboxed import Outbox, Event
from outboxed.models import metadata

engine = create_engine("postgresql://...")
metadata.create_all(engine)

outbox = Outbox()

with engine.begin() as conn:
    # ... your business write ...
    outbox.enqueue(conn, Event(topic="orders", payload='{"id": 1}'))
```

```python
from outboxed import Relay
from outboxed.backends.in_memory import InMemoryBackend

relay = Relay(engine, backend=InMemoryBackend())
relay.run_forever()
```

## The guarantee

Once a transaction commits, its event is delivered at least once, and
never silently dropped. This is verified by a chaos test
(`tests/test_chaos_crash_recovery.py`) that runs in CI on every commit. See
[docs/guarantees.md](docs/guarantees.md) for exact semantics.

## Backends

Kafka, Redis Streams, and SQS adapters ship built in, alongside an
in-memory one for tests. The core has no required broker dependency — a
backend is a small protocol (`outboxed.backends.base.Backend`) you can
implement yourself. See [docs/backends.md](docs/backends.md).

```bash
pip install outboxed
pip install "outboxed[kafka]"   # or [redis], [sqs]
```

## Status

v0.1.0. Python 3.10+. MIT licensed.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
