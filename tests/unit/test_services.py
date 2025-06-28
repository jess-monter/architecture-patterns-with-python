from typing import List

import pytest
from datetime import date

from allocation.adapters.repository import AbstractRepository
from allocation.domain import model
from allocation.service_layer import services

today = date.today()
tomorrow = date.today().replace(day=today.day + 1)  # Example future date


class FakeRepository(AbstractRepository):
    def __init__(self, batches: List[model.Batch]) -> None:
        self._batches = set(batches)

    def add(self, batch: model.Batch) -> None:
        self._batches.add(batch)

    def get(self, reference: str) -> model.Batch:
        return next((b for b in self._batches if b.reference == reference), None)
    
    def list(self) -> list[model.Batch]:
        return list(self._batches)
    

class FakeSession:
    commited = False

    def commit(self) -> None:
        self.commited = True


def test_add_batch() -> None:
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch(ref="b1", sku="sku1", qty=100, eta=None, repo=repo, session=session)
    assert repo.get("b1") is not None
    assert session.commited


# Rewriting tests using now services.add_batch
# Now we don't depend on the model directly, but through the services layer
def test_allocate_returns_allocation() -> None:
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch(ref="batch1", sku="COMPLICATED-LAMP", qty=100, eta=None, repo=repo, session=session)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku() -> None:
    repo, session = FakeRepository([]), FakeSession()
    with pytest.raises(services.InvalidSku, match="Invalid sku INVALID-SKU"):
        services.allocate("o1", "INVALID-SKU", 10, repo, session)


def test_commits() -> None:
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch(ref="b1", sku="OMINOUS-MIRROR", qty=100, eta=None, repo=repo, session=session)
    services.allocate(orderid="o1", sku="OMINOUS-MIRROR", qty=10, repo=repo, session=session)
    assert session.commited


# Equivalent test to test_prefers_current_stock_batches_to_shipments
# The more low level tests we have, the harder it will be to refactor
def test_prefers_warehouse_batches_to_shipments() -> None:
    in_stock_batch = model.Batch(ref="in-stock-batch", sku="RETRO-CLOCK", qty=100, eta=None)
    shipment_batch = model.Batch(ref="shipment-batch", sku="RETRO-CLOCK", qty=100, eta=tomorrow)
    repo = FakeRepository([in_stock_batch, shipment_batch])
    session = FakeSession()

    services.allocate(orderid="orf", sku="RETRO-CLOCK", qty=10, repo=repo, session=session)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100
