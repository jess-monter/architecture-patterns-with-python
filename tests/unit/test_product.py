from datetime import date

from allocation.domain import model
from allocation.domain import events


def test_records_out_of_stock_event_if_cannot_allocate() -> None:
    batch = model.Batch("batch1", "SMALL-FORK", 10, eta=date.today())
    product = model.Product(sku="SMALL-FORK", batches=[batch])
    product.allocate(model.OrderLine("order1", "SMALL-FORK", 10))

    allocation = product.allocate(model.OrderLine("order2", "SMALL-FORK", 1))

    assert product.events[-1] == events.OutOfStock(sku="SMALL-FORK")
    assert allocation is None

