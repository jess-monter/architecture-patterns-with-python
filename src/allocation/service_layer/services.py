from typing import Optional
from datetime import date

from allocation.domain import model
from allocation.adapters.repository import AbstractRepository

from sqlalchemy.orm import Session

class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    """Check if the SKU is valid by verifying it exists in the list of batches."""
    return sku in {batch.sku for batch in batches}


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], repo: AbstractRepository, session: Session) -> None:
    repo.add(model.Batch(ref=ref, sku=sku, qty=qty, eta=eta))
    session.commit()


def allocate(orderid: str, sku: str, qty: int, repo: AbstractRepository, session: Session) -> Optional[str]:
    line = model.OrderLine(orderid=orderid, sku=sku, qty=qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batch_ref: Optional[str] = model.allocate(line, batches)
    session.commit()
    return batch_ref
