from typing import List
from abc import ABC, abstractmethod

import model
from sqlalchemy.orm import Session

class AbstractRepository(ABC):
    @abstractmethod
    def get(self, reference: str) -> model.Batch:
        """Retrieve an entity by its ID."""
        raise NotImplementedError("This method should be overridden in a subclass.")

    @abstractmethod
    def add(self, batch: model.Batch) -> None:
        """Add a new entity to the repository."""
        raise NotImplementedError("This method should be overridden in a subclass.")


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, reference: str) -> model.Batch:
        """Retrieve a batch by its reference."""
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def add(self, batch: model.Batch) -> None:
        """Add a new batch to the repository."""
        self.session.add(batch)

    def list(self) -> List[model.Batch]:
        """List all batches in the repository."""
        return self.session.query(model.Batch).all()