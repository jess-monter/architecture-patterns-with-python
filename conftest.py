
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, clear_mappers, Session
from orm import metadata, start_mappers


@pytest.fixture
def in_memory_db() -> Engine:
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db: Engine) -> Generator[Session, None, None]:
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()
