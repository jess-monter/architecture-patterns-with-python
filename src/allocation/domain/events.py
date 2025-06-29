from dataclasses import dataclass


class Event:
    """Base class for all events."""
    pass

@dataclass
class OutOfStock(Event):
    """Event indicating that an item is out of stock."""
    sku: str
