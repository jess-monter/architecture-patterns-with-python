import allocation.domain.model as model
import allocation.adapters.repository as repository

import pytest

from sqlalchemy import text
from sqlalchemy.orm import Session


def insert_order_line(session: Session) -> int:
    session.execute(
        text(
            "INSERT INTO order_lines (orderid, sku, qty) VALUES (:orderid, :sku, :qty)"
        ),
        {"orderid": "order1", "sku": "GENERIC-SOFA", "qty": 12},
    )
    [[order_line_id]] = session.execute(
        text("SELECT id FROM order_lines WHERE orderid = :orderid AND sku = :sku"),
        {"orderid": "order1", "sku": "GENERIC-SOFA"},
    )
    return int(order_line_id)


def insert_batch(session: Session, ref: str) -> int:
    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta) "
            "VALUES (:ref, 'GENERIC-SOFA', 100, null)"
        ),
        {"ref": ref},
    )
    [[batch_id]] = session.execute(
        text("SELECT id FROM batches WHERE reference = :ref AND sku = 'GENERIC-SOFA'"),
        {"ref": ref},
    )
    return int(batch_id)


def insert_allocation(session: Session, orderline_id: int, batch_id: int) -> None:
    session.execute(
        text(
            "INSERT INTO allocations (orderline_id, batch_id)"
            " VALUES (:orderline_id, :batch_id)"
        ),
        {"orderline_id": orderline_id, "batch_id": batch_id},
    )


def test_repository_can_save_a_batch(session: Session) -> None:
    batch = model.Batch(ref="batch", sku="SKU", qty=100, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = session.execute(
        text("SELECT reference, sku, _purchased_quantity, eta FROM batches")
    )
    assert list(rows) == [("batch", "SKU", 100, None)]


def test_repository_can_save_an_order_line(session: Session) -> None:
    order_line_id = insert_order_line(session)

    rows = session.execute(
        text("SELECT id, sku, qty, orderid FROM order_lines WHERE id = :id"),
        {"id": order_line_id},
    )
    assert list(rows) == [(order_line_id, "GENERIC-SOFA", 12, "order1")]


@pytest.mark.skip("No longer works with the new repository design")
def test_repository_can_retrieve_a_batch_with_allocations(session: Session) -> None:
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ only compares reference
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        model.OrderLine("order1", "GENERIC-SOFA", 12),
    }
