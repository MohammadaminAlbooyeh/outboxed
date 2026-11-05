# Writing a new Backend adapter

A backend is anything that implements the `Backend` protocol in
`outboxed/backends/base.py`:

```python
from typing import Protocol

class Backend(Protocol):
    def publish(self, *, topic: str, key: str | None, payload: str) -> None:
        ...
```

That's the entire contract. `publish` is called once per outbox row, in
creation order, by the relay. Raise an exception to signal failure — the
relay will leave that row undelivered and retry it on the next poll.

## Example: a minimal webhook backend

```python
import httpx

class WebhookBackend:
    def __init__(self, url: str):
        self._url = url

    def publish(self, *, topic: str, key: str | None, payload: str) -> None:
        response = httpx.post(self._url, json={"topic": topic, "key": key, "payload": payload})
        response.raise_for_status()
```

## Guidelines

- Keep broker SDK imports inside the adapter module, not in `outboxed`'s
  core, so the core has no required dependency on any specific broker.
- Don't swallow exceptions — let them propagate so the relay retries.
- If your broker needs a flush/sync step (as Kafka producers do), do it
  inside `publish` so the call only returns once delivery is confirmed (or
  failed) to the broker.
- Add your adapter under `src/outboxed/backends/`, with an optional extra
  in `pyproject.toml` if it needs a broker SDK, and a corresponding test
  under `tests/backends/`.
