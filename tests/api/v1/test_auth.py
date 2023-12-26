import pytest

from fastapi.testclient import TestClient
from fastapi import FastAPI

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.tables.user import User
from app.db.tables.user_session import UserSession
from app.core.config import settings
from tests.api.test_case import TestUserMixit


class TestAuthApi(TestUserMixit):
    @pytest.mark.asyncio
    async def test_login_logout_session(
        self, db_session: Session, client: TestClient, app: FastAPI
    ):
        await self._setup(db_session)
        async with db_session() as session:
            stmt = func.count(UserSession.id)
            count = await session.scalar(stmt)
            assert count == 0
        # login user
        url = settings.TOKEN_URL
        post_date = {"username": "testuser@example.com", "password": "123"}
        response = client.post(url, data=post_date)
        assert response.status_code == 200
        auth_res = response.json()
        assert "access_token" in auth_res.keys()
        return auth_res["access_token"]

        async with db_session() as session:
            stmt = func.count(UserSession.id)
            count = await session.scalar(stmt)
            assert count == 1
        # logout
        url = app.url_path_for("logout")

        await self._teardown(db_session)
        response = client.get(url)
        assert response.status_code == 200

        async with db_session() as session:
            stmt = func.count(UserSession.id)
            count = await session.scalar(stmt)
            assert count == 0

    @pytest.mark.asyncio
    async def test_create_user(
        self, db_session: Session, client: TestClient, app: FastAPI
    ):
        """Регистрация пользователя"""
        await self._setup(db_session)
        async with db_session() as session:
            stmt = func.count(User.id)
            count = await session.scalar(stmt)
            assert count == 1

        url = app.url_path_for("create_user")
        post_date = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "testuser2@example.com",
            "password": "12345",
        }
        response = client.post(url, json=post_date)
        assert response.status_code == 200

        async with db_session() as session:
            stmt = func.count(User.id)
            count = await session.scalar(stmt)
            assert count == 2

        await self._teardown(db_session)
