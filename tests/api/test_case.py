import pytest

from fastapi.testclient import TestClient

from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.db.tables.user import User
from app.db.tables.user_session import UserSession
from app.core.config import settings
from app.services.user import create_user_service
from app.schemas.request.user import CreateUserInRequest


class TestAuthMixin:
    def _auth_token(self, client: TestClient):
        response = client.post(
            url=settings.TOKEN_URL,
            data={"username": "testuser@example.com", "password": "123"},
        )
        auth_res = response.json()
        assert response.status_code == 200
        assert "access_token" in auth_res.keys()
        return auth_res["access_token"]


class TestUserMixit:
    @pytest.mark.asyncio
    async def _setup(self, db_session: Session):
        async with db_session() as session:
            stmt = select(User)
            user = await session.scalar(stmt)

        if not user:
            user = await create_user_service(
                async_session=db_session,
                create_user=CreateUserInRequest(
                    first_name="TestUserName",
                    last_name="TestLastName",
                    email="testuser@example.com",
                    password="123",
                ),
            )
        return user

    @pytest.mark.asyncio
    async def _teardown(self, db_session: Session):
        """clear db"""
        async with db_session() as session:
            await session.execute(delete(UserSession))
            await session.execute(delete(User))
            await session.commit()
