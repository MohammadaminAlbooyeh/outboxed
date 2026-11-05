"""In-process backend for tests and for trying the library with no broker."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _PublishedMessage:
    topic: str
    key: str | None
    payload: str


class InMemoryBackend:
    """Collects published messages in memory instead of talking to a broker."""

    def __init__(self) -> None:
        self.messages: list[_PublishedMessage] = []

    def publish(self, *, topic: str, key: str | None, payload: str) -> None:
        self.messages.append(_PublishedMessage(topic=topic, key=key, payload=payload))
