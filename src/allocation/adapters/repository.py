from typing import List
from abc import ABC, abstractmethod

import allocation.domain.model as model
from sqlalchemy.orm import Session


class AbstractRepository(ABC):
    @abstractmethod
    def get(self, sku: str) -> model.Product:
        """Retrieve an entity by its ID."""
        raise NotImplementedError("This method should be overridden in a subclass.")

    @abstractmethod
    def add(self, product: model.Product) -> None:
        """Add a new entity to the repository."""
        raise NotImplementedError("This method should be overridden in a subclass.")
    
    @abstractmethod
    def list(self) -> List[model.Batch]:
        """List all entities in the repository."""
        raise NotImplementedError("This method should be overridden in a subclass.")


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, sku: str) -> model.Product:
        """Retrieve a batch by its reference."""
        return self.session.query(model.Product).filter_by(sku=sku).first()

    def add(self, product: model.Product) -> None:
        """Add a new batch to the repository."""
        self.session.add(product)

    def list(self) -> List[model.Batch]:
        """List all batches in the repository."""
        return self.session.query(model.Batch).all()