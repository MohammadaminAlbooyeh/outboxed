"""Unit tests for the Redis Streams backend, using a fake client (no broker needed)."""

from outboxed.backends.redis_streams import RedisStreamsBackend


class FakeRedisClient:
    def __init__(self):
        self.calls = []

    def xadd(self, stream, fields):
        self.calls.append((stream, fields))


def test_publish_sends_to_stream():
    client = FakeRedisClient()
    backend = RedisStreamsBackend(client)

    backend.publish(topic="orders", key="order-1", payload='{"id": 1}')

    assert client.calls == [("orders", {"key": "order-1", "payload": '{"id": 1}'})]


def test_publish_applies_stream_prefix():
    client = FakeRedisClient()
    backend = RedisStreamsBackend(client, stream_prefix="prod.")

    backend.publish(topic="orders", key="order-1", payload="payload")

    stream, _ = client.calls[0]
    assert stream == "prod.orders"


def test_publish_defaults_missing_key_to_empty_string():
    client = FakeRedisClient()
    backend = RedisStreamsBackend(client)

    backend.publish(topic="orders", key=None, payload="payload")

    _, fields = client.calls[0]
    assert fields["key"] == ""
