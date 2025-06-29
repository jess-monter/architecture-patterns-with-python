from typing import Optional

from dataclasses import dataclass
from datetime import date

class Command:
    pass


@dataclass
class Allocate(Command):
    """Command to allocate a batch for an order line."""
    orderid: str
    sku: str
    qty: int


@dataclass
class CreateBatch(Command):
    """Command to create a new batch."""
    ref: str
    sku: str
    qty: int
    eta: Optional[date] = None


@dataclass
class ChangeBatchQuantity(Command):
    """Command to change the quantity of a batch."""
    ref: str
    qty: int
