"""Unit tests for the Kafka backend, using a fake producer (no broker needed)."""

import pytest

from outboxed.backends.kafka import KafkaBackend, KafkaDeliveryError


class FakeKafkaProducer:
    def __init__(self, *, delivery_error=None, pending=0):
        self.calls = []
        self._delivery_error = delivery_error
        self._pending = pending

    def produce(self, topic, *, key, value, on_delivery):
        self.calls.append({"topic": topic, "key": key, "value": value})
        on_delivery(self._delivery_error, None)

    def flush(self, timeout):
        return self._pending


def test_publish_sends_to_topic():
    producer = FakeKafkaProducer()
    backend = KafkaBackend(producer)

    backend.publish(topic="orders", key="order-1", payload='{"id": 1}')

    assert producer.calls == [{"topic": "orders", "key": b"order-1", "value": b'{"id": 1}'}]


def test_publish_sends_none_key_when_key_is_none():
    producer = FakeKafkaProducer()
    backend = KafkaBackend(producer)

    backend.publish(topic="orders", key=None, payload="payload")

    assert producer.calls[0]["key"] is None


def test_publish_raises_on_delivery_error():
    producer = FakeKafkaProducer(delivery_error="broker unavailable")
    backend = KafkaBackend(producer)

    with pytest.raises(KafkaDeliveryError, match="broker unavailable"):
        backend.publish(topic="orders", key=None, payload="payload")


def test_publish_raises_when_messages_still_pending_after_flush():
    producer = FakeKafkaProducer(pending=1)
    backend = KafkaBackend(producer)

    with pytest.raises(KafkaDeliveryError, match="still pending"):
        backend.publish(topic="orders", key=None, payload="payload")
