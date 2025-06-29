from typing import List, Set
from abc import ABC, abstractmethod

from allocation.adapters import orm
import allocation.domain.model as model
from sqlalchemy.orm import Session


class AbstractRepository(ABC):
    def __init__(self) -> None:
        self.seen: Set[model.Product] = set()

    def get(self, sku: str) -> model.Product:
        """Retrieve a product by its SKU."""
        product = self._get(sku)
        if product:
            self.seen.add(product)
        return product
    
    def add(self, product: model.Product) -> None:
        """Add a new product to the repository."""
        self._add(product)
        self.seen.add(product)

    def get_by_batchref(self, batchref: str) -> model.Product:
        product = self._get_by_batchref(batchref)
        if product:
            self.seen.add(product)
        return product

    @abstractmethod
    def _add(self, product: model.Product) -> None:
        """Add a new entity to the repository."""
        raise NotImplementedError

    @abstractmethod
    def _get(self, sku: str) -> model.Product:
        """Retrieve an entity by its ID."""
        raise NotImplementedError
    
    @abstractmethod
    def _get_by_batchref(self, batchref: str) -> model.Product:
        """Retrieve a product by its batch reference."""
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session

    def _get(self, sku: str) -> model.Product:
        """Retrieve a batch by its reference."""
        return self.session.query(model.Product).filter_by(sku=sku).first()

    def _add(self, product: model.Product) -> None:
        """Add a new batch to the repository."""
        self.session.add(product)

    def _get_by_batchref(self, batchref: str) -> model.Product:
        return (
            self.session.query(model.Product)
            .join(model.Batch)
            .filter(orm.batches.c.reference == batchref)
            .first()
        )
