
from typing import Generator
import time
from pathlib import Path

import requests


import pytest
import redis
from sqlalchemy import create_engine
from sqlalchemy import Engine, Connection
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, clear_mappers
from tenacity import retry, stop_after_delay

from allocation.adapters.orm import metadata, start_mappers
from allocation import config


@retry(stop=stop_after_delay(10))
def wait_for_postgres_to_come_up(engine):
    return engine.connect()


@retry(stop=stop_after_delay(10))
def wait_for_webapp_to_come_up() -> requests.Response:
    return requests.get(config.get_api_url())


@retry(stop=stop_after_delay(10))
def wait_for_redis_to_come_up() -> bool:
    print("Waiting for Redis to come up...")
    r = redis.Redis(**config.get_redis_host_and_port())
    return bool(r.ping())


@pytest.fixture
def in_memory_db() -> Engine:
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_db: Engine) -> Generator[sessionmaker, None, None]:
    start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture
def session(session_factory: sessionmaker) -> sessionmaker:
    return session_factory()


@pytest.fixture(scope="session")
def postgres_db() -> Engine:
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session_factory(postgres_db: Engine) -> Generator[sessionmaker, None, None]:
    start_mappers()
    yield sessionmaker(bind=postgres_db)
    clear_mappers()


@pytest.fixture
def postgres_session(postgres_session_factory: sessionmaker) -> sessionmaker:
    return postgres_session_factory()


@pytest.fixture
def restart_api() -> None:
    (Path(__file__).parent / "flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


@pytest.fixture
def restart_redis_pubsub() -> None:
    wait_for_redis_to_come_up()
