from typing import Optional

from allocation.adapters import email, redis_eventpublisher
from allocation.domain import events, model, commands
from allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    """Exception raised for invalid SKU."""
    pass


def add_batch(cmd: commands.CreateBatch, uow: unit_of_work.AbstractUnitOfWork) -> None:
    """Handle the BatchCreated event to add a new batch."""
    with uow:
        product = uow.products.get(sku=cmd.sku)
        if product is None:
            product = model.Product(sku=cmd.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(ref=cmd.ref, sku=cmd.sku, qty=cmd.qty, eta=cmd.eta))
        uow.commit()


def allocate(cmd: commands.Allocate, uow: unit_of_work.AbstractUnitOfWork) -> Optional[str]:
    """Handle the AllocationRequired event to allocate a batch."""
    line = model.OrderLine(orderid=cmd.orderid, sku=cmd.sku, qty=cmd.qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batch_ref = product.allocate(line)
        uow.commit()
    return batch_ref


def change_batch_quantity(cmd: commands.ChangeBatchQuantity, uow: unit_of_work.AbstractUnitOfWork) -> None:
    with uow:
        product = uow.products.get_by_batchref(batchref=cmd.ref)
        product.change_batch_quantity(ref=cmd.ref, qty=cmd.qty)
        uow.commit()


def send_out_of_stock_notification(
    event: events.OutOfStock,
    uow: unit_of_work.AbstractUnitOfWork, # noqa: ARG001
) -> None:
    email.send_mail(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )


def publish_allocated_event(event: events.Allocated, uow: unit_of_work.AbstractUnitOfWork) -> None:
    """Publish the Allocated event."""
    redis_eventpublisher.publish("line_allocated", event)
