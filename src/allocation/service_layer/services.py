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
        product = uow.products.get(sku=sku)
        if product is None:
            product = model.Product(sku=sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(ref=ref, sku=sku, qty=qty, eta=eta))
        uow.commit()


def allocate(orderid: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork) -> Optional[str]:
    line = model.OrderLine(orderid=orderid, sku=sku, qty=qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batch_ref: Optional[str] = product.allocate(line)
        uow.commit()
    return batch_ref
