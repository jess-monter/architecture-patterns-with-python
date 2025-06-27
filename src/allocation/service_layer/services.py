from allocation.domain import model
from allocation.adapters.repository import AbstractRepository

from sqlalchemy.orm import Session

class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    """Check if the SKU is valid by verifying it exists in the list of batches."""
    return sku in {batch.sku for batch in batches}


def allocate(line: model.OrderLine, repo: AbstractRepository, session: Session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batch_ref: str = model.allocate(line, batches)
    session.commit()
    return batch_ref
