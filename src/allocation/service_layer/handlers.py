from typing import Optional

from allocation.adapters import email
from allocation.domain import events, model
from allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    """Exception raised for invalid SKU."""
    pass


def add_batch(event: events.BatchCreated, uow: unit_of_work.AbstractUnitOfWork) -> None:
    """Handle the BatchCreated event to add a new batch."""
    with uow:
        product = uow.products.get(sku=event.sku)
        if product is None:
            product = model.Product(sku=event.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(ref=event.ref, sku=event.sku, qty=event.qty, eta=event.eta))
        uow.commit()


def allocate(event: events.AllocationRequired, uow: unit_of_work.AbstractUnitOfWork) -> Optional[str]:
    """Handle the AllocationRequired event to allocate a batch."""
    line = model.OrderLine(orderid=event.orderid, sku=event.sku, qty=event.qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batch_ref = product.allocate(line)
        uow.commit()
    return batch_ref


def change_batch_quantity(event: events.BatchQuantityChanged, uow: unit_of_work.AbstractUnitOfWork) -> None:
    with uow:
        product = uow.products.get_by_batchref(batchref=event.ref)
        product.change_batch_quantity(ref=event.ref, qty=event.qty)
        uow.commit()


def send_out_of_stock_notification(
    event: events.OutOfStock,
    uow: unit_of_work.AbstractUnitOfWork, # noqa: ARG001
) -> None:
    email.send_mail(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )
