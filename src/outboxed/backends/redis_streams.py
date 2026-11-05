"""Redis Streams backend. Requires the ``outboxed[redis]`` extra."""

from __future__ import annotations

from typing import Any


class RedisStreamsBackend:
    """Publishes outbox entries to a Redis stream via XADD."""

    def __init__(self, client: Any, *, stream_prefix: str = "") -> None:
        self._client = client
        self._stream_prefix = stream_prefix

    def publish(self, *, topic: str, key: str | None, payload: str) -> None:
        stream = f"{self._stream_prefix}{topic}"
        self._client.xadd(stream, {"key": key or "", "payload": payload})
