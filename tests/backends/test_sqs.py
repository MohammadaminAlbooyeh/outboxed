"""Unit tests for the SQS backend, using a fake client (no AWS needed)."""

import pytest

from outboxed.backends.sqs import SQSBackend


class FakeSQSClient:
    def __init__(self):
        self.calls = []

    def send_message(self, **kwargs):
        self.calls.append(kwargs)


def test_publish_sends_to_mapped_queue_url():
    client = FakeSQSClient()
    backend = SQSBackend(client, queue_urls={"orders": "https://sqs.example/orders"})

    backend.publish(topic="orders", key="order-1", payload='{"id": 1}')

    assert client.calls == [
        {
            "QueueUrl": "https://sqs.example/orders",
            "MessageBody": '{"id": 1}',
            "MessageGroupId": "order-1",
        }
    ]


def test_publish_omits_message_group_id_when_key_is_none():
    client = FakeSQSClient()
    backend = SQSBackend(client, queue_urls={"orders": "https://sqs.example/orders"})

    backend.publish(topic="orders", key=None, payload="payload")

    assert "MessageGroupId" not in client.calls[0]


def test_publish_raises_on_unmapped_topic():
    client = FakeSQSClient()
    backend = SQSBackend(client, queue_urls={"orders": "https://sqs.example/orders"})

    with pytest.raises(KeyError):
        backend.publish(topic="unknown", key=None, payload="payload")
