"""Kafka backend. Requires the ``outboxed[kafka]`` extra."""

from __future__ import annotations

from typing import Any


class KafkaDeliveryError(RuntimeError):
    """Raised when confluent-kafka reports a failed delivery."""


class KafkaBackend:
    """Publishes outbox entries to a Kafka topic via confluent-kafka."""

    def __init__(self, producer: Any, *, flush_timeout: float = 10.0) -> None:
        self._producer = producer
        self._flush_timeout = flush_timeout

    def publish(self, *, topic: str, key: str | None, payload: str) -> None:
        delivery_error: Any = None

        def on_delivery(err: Any, _msg: Any) -> None:
            nonlocal delivery_error
            delivery_error = err

        self._producer.produce(
            topic,
            key=key.encode() if key is not None else None,
            value=payload.encode(),
            on_delivery=on_delivery,
        )

        pending = self._producer.flush(self._flush_timeout)
        if pending:
            raise KafkaDeliveryError(
                f"{pending} message(s) still pending after {self._flush_timeout}s flush timeout"
            )
        if delivery_error is not None:
            raise KafkaDeliveryError(str(delivery_error))
