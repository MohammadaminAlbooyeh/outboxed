"""The in-memory backend just records what it's given."""

from outboxed.backends.in_memory import InMemoryBackend


def test_publish_records_message():
    backend = InMemoryBackend()

    backend.publish(topic="orders", key="order-1", payload='{"id": 1}')

    assert len(backend.messages) == 1
    message = backend.messages[0]
    assert message.topic == "orders"
    assert message.key == "order-1"
    assert message.payload == '{"id": 1}'
