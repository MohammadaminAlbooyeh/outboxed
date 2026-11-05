"""Broker adapters implementing the Backend protocol."""

from outboxed.backends.base import Backend
from outboxed.backends.in_memory import InMemoryBackend

__all__ = ["Backend", "InMemoryBackend"]
