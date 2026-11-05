"""OutboxEntry table definition and the Event the caller enqueues."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy import Column, DateTime, MetaData, String, Table, func

metadata = MetaData()

outbox_table = Table(
    "outboxed_entries",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("topic", String(255), nullable=False),
    Column("key", String(255), nullable=True),
    Column("payload", String, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("delivered_at", DateTime(timezone=True), nullable=True),
)


@dataclass(frozen=True)
class Event:
    """A single event to be delivered to a backend, exactly once observable."""

    topic: str
    payload: str
    key: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
