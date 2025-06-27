from typing import List

import pytest

from allocation.adapters.repository import AbstractRepository
from allocation.domain import model
from allocation.service_layer import services


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


def test_returns_allocation():
    line = model.OrderLine(orderid="o1", sku="sku1", qty=10)
    batch = model.Batch(ref="b1", sku="sku1", qty=100, eta=None)
    repo = FakeRepository([batch])
    result = services.allocate(line, repo, FakeSession())

    assert result == "b1"

def test_error_for_invalid_sku():
    line = model.OrderLine(orderid="o1", sku="NONEXISTENTSKU", qty=10)
    batch = model.Batch(ref="b1", sku="AREALSKU", qty=100, eta=None)
    repo = FakeRepository([batch])
    
    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())

def test_commits():
    line = model.OrderLine(orderid="o1", sku="sku1", qty=10)
    batch = model.Batch(ref="b1", sku="sku1", qty=100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)

    assert session.commited is True
