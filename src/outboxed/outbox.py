"""The write side: enqueue an event inside the caller's own transaction."""

from __future__ import annotations

from sqlalchemy.engine import Connection

from outboxed.models import Event, outbox_table


class Outbox:
    """Writes events into the outbox table using the caller's connection.

    Call ``enqueue`` with the same ``Connection``/transaction used for the
    business write. If that transaction rolls back, the event never existed.
    """

    def enqueue(self, connection: Connection, event: Event) -> None:
        connection.execute(
            outbox_table.insert().values(
                id=event.id,
                topic=event.topic,
                key=event.key,
                payload=event.payload,
            )
        )
