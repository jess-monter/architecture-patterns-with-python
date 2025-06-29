from typing import List, Set
from abc import ABC, abstractmethod

import allocation.domain.model as model
from sqlalchemy.orm import Session


class AbstractRepository(ABC):
    def __init__(self) -> None:
        self.seen: Set[model.Product] = set()

    @abstractmethod
    def _get(self, sku: str) -> model.Product:
        """Retrieve an entity by its ID."""
        raise NotImplementedError("This method should be overridden in a subclass.")

    @abstractmethod
    def _add(self, product: model.Product) -> None:
        """Add a new entity to the repository."""
        raise NotImplementedError("This method should be overridden in a subclass.")
    
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
    
    @abstractmethod
    def list(self) -> List[model.Batch]:
        """List all entities in the repository."""
        raise NotImplementedError("This method should be overridden in a subclass.")


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

    def list(self) -> List[model.Batch]:
        """List all batches in the repository."""
        return self.session.query(model.Batch).all()