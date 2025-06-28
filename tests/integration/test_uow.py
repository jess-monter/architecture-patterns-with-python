from typing import Callable, Optional
from datetime import date

import pytest
from allocation.domain import model
from allocation.service_layer import unit_of_work
from sqlalchemy import text
from sqlalchemy.orm import Session


def insert_batch(session: Session, ref: str, sku: str, qty: int, eta: Optional[date]) -> None:
    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta) "
            "VALUES (:ref, :sku, :qty, :eta)"
        ),
        {"ref": ref, "sku": sku, "qty": qty, "eta": eta},
    )


def get_allocated_batch_ref(session: Session, orderid: str, sku: str) -> Optional[str]:
    [[orderline_id]] = session.execute(
        text(
            "SELECT id FROM order_lines b WHERE orderid = :orderid AND sku = :sku"
        ),
        {"orderid": orderid, "sku": sku},
    )
    [[batch_ref]] = session.execute(
        text(
            "SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id"
            " WHERE orderline_id = :orderline_id"
        ),
        {"orderline_id": orderline_id},
    )

    return batch_ref if batch_ref else None


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory: Callable) -> None:
    session = session_factory()
    insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)

    with uow:
        batch = uow.batches.get(reference="batch1")
        line = model.OrderLine(orderid="o1", sku="HIPSTER-WORKBENCH", qty=10)
        batch.allocate(line)
        uow.commit()

    batchref = get_allocated_batch_ref(session, "o1", "HIPSTER-WORKBENCH")
    assert batchref == "batch1"


def test_rolls_back_uncommitted_work_by_default(session_factory: Callable) -> None:
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, "batch1", "MEDIUM-PLINTH", 100, None)

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []


def test_rolls_back_on_error(session_factory: Callable) -> None:
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, "batch1", "LARGE-FORK", 100, None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))

    assert rows == []
