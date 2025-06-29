from typing import Callable, Dict, List, Type

from allocation.domain import events
from allocation.adapters import email


def handle(event: events.Event) -> None:
    for handler in HANDLERS[type(event)]:
        handler(event)


def send_out_of_stock_notification(event: events.OutOfStock) -> None:
    email.send_mail(
        "sample@sample.com",
        f"Out of stock for {event.sku}",
    )


HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.OutOfStock: [send_out_of_stock_notification],

}
