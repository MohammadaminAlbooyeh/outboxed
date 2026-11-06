# outboxed

The transactional outbox pattern for Python backends: reliably publish an
event every time — and only when — a database write actually commits.

## Install

```bash
pip install outboxed
# or, with a broker adapter's optional extra:
pip install "outboxed[kafka]"
```

## Quickstart

```python
from sqlalchemy import create_engine
from outboxed import Outbox, Event
from outboxed.models import metadata

engine = create_engine("postgresql://...")
metadata.create_all(engine)

outbox = Outbox()

with engine.begin() as conn:
    # ... your business write, e.g. inserting an order row ...
    outbox.enqueue(conn, Event(topic="orders", payload='{"id": 1}'))
```

Run a relay process separately to deliver enqueued events to a backend:

```python
from outboxed import Relay
from outboxed.backends.in_memory import InMemoryBackend

relay = Relay(engine, backend=InMemoryBackend())
relay.run_forever()
```

## Further reading

- [Quickstart](quickstart.md)
- [The dual-write problem](dual-write-problem.md)
- [Delivery guarantees](guarantees.md)
- [Writing a backend adapter](backends.md)
