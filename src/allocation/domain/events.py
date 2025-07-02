from dataclasses import dataclass


@dataclass
class Event:
    """Base class for all events."""
    pass

@dataclass
class OutOfStock(Event):
    """Event indicating that an item is out of stock."""
    sku: str


@dataclass
class Allocated(Event):
    """Event indicating that an order has been allocated to a batch."""
    orderid: str
    sku: str
    qty: int
    batchref: str


@dataclass
class Deallocated(Event):
    """Event indicating that an order has been deallocated from a batch."""
    orderid: str
    sku: str
    qty: int
