from typing import Any

from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey, event
from sqlalchemy.orm import relationship
from sqlalchemy.orm import registry

import allocation.domain.model as model


metadata = MetaData()
mapper_registry = registry()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)

product = Table(
    "products",
    metadata,
    Column("sku", String(255), primary_key=True),
    Column("version_number", Integer, nullable=False, default=0),
)

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", ForeignKey("products.sku")),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


allocations_view = Table(
    "allocations_view",
    metadata,
    Column("orderid", String(255)),
    Column("sku", String(255)),
    Column("batchref", String(255)),
)


def start_mappers() -> None:
    """Map the model classes to the database tables."""
    mapper_registry.map_imperatively(model.OrderLine, order_lines)
    mapper_registry.map_imperatively(
        model.Batch,
        batches,
        properties={
            "_allocations": relationship(
                model.OrderLine, secondary=allocations, collection_class=set,
            ),
            "product": relationship(model.Product, back_populates="batches")
        },
    )
    mapper_registry.map_imperatively(
        model.Product,
        product,
        properties={
            "batches": relationship(model.Batch, back_populates="product"),
        },
    )


@event.listens_for(model.Product, "load")
def receive_load(product: model.Product, _: Any) -> None:
    product.events = []
