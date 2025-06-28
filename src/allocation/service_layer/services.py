from typing import Optional
from datetime import date

from allocation.domain import model
from allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    """Check if the SKU is valid by verifying it exists in the list of batches."""
    return sku in {batch.sku for batch in batches}


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], uow: unit_of_work.AbstractUnitOfWork) -> None:
    with uow:
        uow.batches.add(model.Batch(ref=ref, sku=sku, qty=qty, eta=eta))
        uow.commit()


def allocate(orderid: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork) -> Optional[str]:
    line = model.OrderLine(orderid=orderid, sku=sku, qty=qty)
    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        batch_ref: Optional[str] = model.allocate(line, batches)
        uow.commit()
    return batch_ref
