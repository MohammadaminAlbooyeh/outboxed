"""Kafka backend. Requires the ``outboxed[kafka]`` extra."""

from __future__ import annotations

from typing import Any


class KafkaBackend:
    """Publishes outbox entries to a Kafka topic via confluent-kafka."""

    def __init__(self, producer: Any, *, flush_timeout: float = 10.0) -> None:
        self._producer = producer
        self._flush_timeout = flush_timeout

    def publish(self, *, topic: str, key: str | None, payload: str) -> None:
        self._producer.produce(
            topic,
            key=key.encode() if key is not None else None,
            value=payload.encode(),
        )
        self._producer.flush(self._flush_timeout)
