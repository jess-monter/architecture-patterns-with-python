from typing import Optional
from datetime import date
from dataclasses import dataclass


class Event:
    """Base class for all events."""
    pass

@dataclass
class OutOfStock(Event):
    """Event indicating that an item is out of stock."""
    sku: str


@dataclass
class BatchCreated(Event):
    """Event indicating that a new batch has been created."""
    ref: str
    sku: str
    qty: int
    eta: Optional[date] = None


@dataclass
class AllocationRequired(Event):
    """Event indicating that an allocation is required."""
    orderid: str
    sku: str
    qty: int


@dataclass
class BatchQuantityChanged(Event):
    """Event indicating that the quantity of a batch has changed."""
    ref: str
    qty: int
