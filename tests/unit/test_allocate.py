from datetime import date
from allocation.domain.model import Batch, OrderLine, allocate, OutOfStock

import pytest

today = date.today()
tomorrow = today.replace(day=today.day + 1)
later = today.replace(day=today.day + 2)


def test_prefers_current_stock_batches_to_shipments() -> None:
    in_stock_batch = Batch("batch-001", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("batch-002", "RETRO-CLOCK", 100, eta=tomorrow)
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_prefers_earlier_batches() -> None:
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    line = OrderLine("oref", "MINIMALIST-SPOON", 10)

    allocate(line, [medium, latest, earliest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100

def test_returns_allocated_batch_ref() -> None:
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference

def test_raises_out_of_stock_exception_if_cannot_allocate() -> None:
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    allocate(OrderLine("oref", "SMALL-FORK", 10), [batch])

    with pytest.raises(OutOfStock):
        allocate(OrderLine("oref", "SMALL-FORK", 1), [batch])