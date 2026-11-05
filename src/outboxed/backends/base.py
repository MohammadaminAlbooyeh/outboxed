"""The protocol every broker adapter implements."""

from __future__ import annotations

from typing import Protocol


class Backend(Protocol):
    """A destination the relay publishes outbox entries to."""

    def publish(self, *, topic: str, key: str | None, payload: str) -> None:
        """Publish one entry. Raise to signal failure; the relay will retry."""
        ...
