"""A minimal order API using outboxed end-to-end.

Run Postgres via ../docker-compose.yml, then:

    uvicorn main:app --reload

POST /orders inserts an order row and enqueues an "order.placed" event in
the same transaction. Run relay.py separately to deliver it.
"""

from __future__ import annotations

import json

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine

from outboxed import Event, Outbox
from outboxed.models import metadata as outbox_metadata

DATABASE_URL = "postgresql://outboxed:outboxed@localhost:5432/outboxed"

engine = create_engine(DATABASE_URL)
app_metadata = MetaData()

orders_table = Table(
    "orders",
    app_metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("item", String, nullable=False),
)

outbox = Outbox()
app = FastAPI(title="outboxed example: order service")


class OrderRequest(BaseModel):
    item: str


@app.on_event("startup")
def create_tables() -> None:
    app_metadata.create_all(engine)
    outbox_metadata.create_all(engine)


@app.post("/orders")
def place_order(order: OrderRequest) -> dict:
    with engine.begin() as conn:
        result = conn.execute(orders_table.insert().values(item=order.item))
        order_id = result.inserted_primary_key[0]

        outbox.enqueue(
            conn,
            Event(topic="order.placed", key=str(order_id), payload=json.dumps({
                "order_id": order_id,
                "item": order.item,
            })),
        )

    return {"id": order_id, "item": order.item}
