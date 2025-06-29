from __future__ import annotations

from typing import Any
from abc import ABC, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from allocation import config
from allocation.adapters import repository
from allocation.service_layer import messagebus

class AbstractUnitOfWork(ABC):
    products: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.rollback()

    def commit(self) -> None:
        self._commit()
        self.publish_events()

    def publish_events(self) -> None:
        for product in self.products.seen:
            while product.events:
                event = product.events.pop(0)
                messagebus.handle(event)

    @abstractmethod
    def _commit(self) -> None:
        """Commit the current transaction."""
        raise NotImplementedError
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        raise NotImplementedError
    

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
        isolation_level="REPEATABLE READ",
    )
)

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: sessionmaker = DEFAULT_SESSION_FACTORY) -> None:
        self.session_factory = session_factory

    def __enter__(self) -> AbstractUnitOfWork:
        self.session = self.session_factory() # type: Session
        self.products = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()
    
    def __exit__(self, *args: Any) -> None:
        super().__exit__(*args)
        self.session.close()

    def _commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()

