"""SQS backend. Requires the ``outboxed[sqs]`` extra."""

from __future__ import annotations

from typing import Any


class SQSBackend:
    """Publishes outbox entries to an SQS queue via send_message.

    ``topic`` is mapped to a queue URL through ``queue_urls`` since SQS has
    no native topic concept.
    """

    def __init__(self, client: Any, *, queue_urls: dict[str, str]) -> None:
        self._client = client
        self._queue_urls = queue_urls

    def publish(self, *, topic: str, key: str | None, payload: str) -> None:
        queue_url = self._queue_urls[topic]
        kwargs: dict[str, Any] = {"QueueUrl": queue_url, "MessageBody": payload}
        if key is not None:
            kwargs["MessageGroupId"] = key
        self._client.send_message(**kwargs)
