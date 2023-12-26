import os
from typing import Any, Generator

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.db.tables.base import Base as DBBase
from app.main import get_application
from app.api.dependencies.database import AsyncSession, get_session


SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite://")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # , connect_args={"check_same_thread": False}
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    try:
        create_database(engine.url)
    except Exception:
        pass
    DBBase.metadata.create_all(engine)  # Create the tables.
    _app = get_application()
    yield _app
    DBBase.metadata.drop_all(engine)


async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    future=True,
)


@pytest.fixture
def db_session(app: FastAPI) -> Generator[AsyncSession, Any, None]:
    try:
        yield AsyncSessionLocal
    except SQLAlchemyError:
        pass


@pytest.fixture()
def client(app: FastAPI, db_session: AsyncSession) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_session] = _get_test_db
    with TestClient(app) as client:
        yield client
