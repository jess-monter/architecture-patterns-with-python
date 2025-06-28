
from typing import Generator
import time
from pathlib import Path

import requests
from requests.exceptions import ConnectionError

import pytest
from sqlalchemy import create_engine
from sqlalchemy import Engine, Connection
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, clear_mappers, Session
from allocation.adapters.orm import metadata, start_mappers
from allocation import config


def wait_for_postgres_to_come_up(engine: Engine) -> Connection:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


def wait_for_webapp_to_come_up() -> requests.Response:
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


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


@pytest.fixture(scope="session")
def postgres_db() -> Engine:
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db: Engine) -> Generator[Session, None, None]:
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture
def restart_api() -> None:
    (Path(__file__).parent / "flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
