from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional, Type, Union, Any

from allocation.domain import events, commands
from allocation.adapters import email
from allocation.service_layer import unit_of_work
from allocation.service_layer import handlers


logger = logging.getLogger(__name__)

Message = Union[events.Event, commands.Command]


def handle(message: Message, uow: unit_of_work.AbstractUnitOfWork) -> List[Optional[str]]:
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f"{message} was not an Event or Command")

    return results

def handle_event(event: events.Event, queue: List[Message], uow: unit_of_work.AbstractUnitOfWork) -> None:
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            logger.debug("Handling event %s with hanlder %s", event, handler)
            handler(event, uow)
            queue.extend(uow.collect_new_events())
        except Exception as e:
            logger.exception("Exception handling event %s", event)
            continue


def handle_command(command: commands.Command, queue: List[Message], uow: unit_of_work.AbstractUnitOfWork) -> Optional[Any]:
    logger.debug("Handling command %s", command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception("Exception handling command %s", command)
        raise


def send_out_of_stock_notification(event: events.OutOfStock) -> None:
    email.send_mail(
        "sample@sample.com",
        f"Out of stock for {event.sku}",
    )


EVENT_HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.Allocated: [handlers.publish_allocated_event, handlers.add_allocation_to_read_model],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
    events.Deallocated: [handlers.remove_allocation_from_read_model, handlers.reallocate],

}


COMMAND_HANDLERS: Dict[Type[commands.Command], Callable] = {
    commands.CreateBatch: handlers.add_batch,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
    commands.Allocate: handlers.allocate,
}
