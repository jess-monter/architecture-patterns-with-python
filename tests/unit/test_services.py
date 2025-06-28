from typing import List

import pytest
from datetime import date

from allocation.adapters.repository import AbstractRepository
from allocation.domain import model
from allocation.service_layer import services, unit_of_work

today = date.today()
tomorrow = date.today().replace(day=today.day + 1)  # Example future date


class FakeRepository(AbstractRepository):
    def __init__(self, products: List[model.Product]) -> None:
        self._products = set(products)

    def add(self, product: model.Product) -> None:
        self._products.add(product)

    def get(self, sku: str) -> model.Batch:
        return next((p for p in self._products if p.sku == sku), None)
    
    def list(self) -> list[model.Product]:
        return list(self._products)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self) -> None:
        self.products = FakeRepository([])
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        """We rollback by default, we need to commit explicitly."""
        pass


def test_add_batch_for_new_product() -> None:
    uow = FakeUnitOfWork()
    services.add_batch(ref="b1", sku="sku1", qty=100, eta=None, uow=uow)
    assert uow.products.get("sku1") is not None
    assert uow.committed


# Rewriting tests using now services.add_batch
# Now we don't depend on the model directly, but through the services layer
def test_allocate_returns_allocation() -> None:
    uow = FakeUnitOfWork()
    services.add_batch(ref="batch1", sku="COMPLICATED-LAMP", qty=100, eta=None, uow=uow)
    result = services.allocate(orderid="o1", sku="COMPLICATED-LAMP", qty=10, uow=uow)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(services.InvalidSku, match="Invalid sku INVALID-SKU"):
        services.allocate(orderid="o1", sku="INVALID-SKU", qty=10, uow=uow)


def test_allocate_commits() -> None:
    uow = FakeUnitOfWork()
    services.add_batch(ref="batch1", sku="COMPLICATED-LAMP", qty=100, eta=None, uow=uow)
    services.allocate(orderid="o1", sku="COMPLICATED-LAMP", qty=10, uow=uow)
    assert uow.committed
