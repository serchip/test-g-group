import pytest

from fastapi.testclient import TestClient
from fastapi import FastAPI

from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import select, delete

from app.db.tables.post import Post
from tests.api.test_case import TestAuthMixin, TestUserMixit
from app.services.post import create_post_service
from app.schemas.request.post import CreatePostInRequest
from app.services.user import create_user_service
from app.schemas.request.user import CreateUserInRequest


class TestPostApi(TestAuthMixin, TestUserMixit):
    @pytest.mark.asyncio
    async def _teardown(self, db_session: Session):
        """clear db"""
        async with db_session() as session:
            await session.execute(delete(Post))
            await session.commit()
        await super()._teardown(db_session)

    @pytest.mark.asyncio
    async def test_add_post(
        self, db_session: Session, client: TestClient, app: FastAPI
    ):
        """Добавить заметку"""
        await self._setup(db_session)
        async with db_session() as session:
            stmt = func.count(Post.id)
            count = await session.scalar(stmt)
            assert count == 0

        url = app.url_path_for("create_post")
        post_date = {
            "title": "Test Post title",
            "description": "Test Post description",
        }
        response = client.post(url, json=post_date)
        assert response.status_code == 401

        token = self._auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(url, headers=headers, json=post_date)
        assert response.status_code == 200
        post_res = response.json()
        assert post_res["title"] == post_date["title"]

        async with db_session() as session:
            stmt = func.count(Post.id)
            count = await session.scalar(stmt)
            assert count == 1

        await self._teardown(db_session)

    @pytest.mark.asyncio
    async def test_get_post(
        self, db_session: Session, client: TestClient, app: FastAPI
    ):
        """Запрос одной записи"""

        current_user = await self._setup(db_session)

        async with db_session() as session:
            stmt = func.count(Post.id)
            count = await session.scalar(stmt)
            assert count == 0

        post = await create_post_service(
            async_session=db_session,
            create_post=CreatePostInRequest(
                title="getPost title",
                description="Test Post description",
            ),
            user_id=current_user.id,
        )

        url = app.url_path_for("get_post", post_id=post.id)
        response = client.get(url)
        assert response.status_code == 401

        token = self._auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(url, headers=headers)
        assert response.status_code == 200
        post_res = response.json()
        assert post_res["title"] == "getPost title"

        url = app.url_path_for("get_post", post_id=5)
        response = client.get(url, headers=headers)
        assert response.status_code == 404

        # проверим что 404 на запрос чужого поста
        user2 = await create_user_service(
            async_session=db_session,
            create_user=CreateUserInRequest(
                first_name="TestUserName2",
                last_name="TestLastName2",
                email="testuser2@example.com",
                password="123",
            ),
        )
        post2 = await create_post_service(
            async_session=db_session,
            create_post=CreatePostInRequest(
                title="getPost title 2",
                description="Test Post description 2",
            ),
            user_id=user2.id,
        )
        url = app.url_path_for("get_post", post_id=post2.id)
        response = client.get(url)
        assert response.status_code == 401

        token = self._auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(url, headers=headers)
        assert response.status_code == 404

        await self._teardown(db_session)

    @pytest.mark.asyncio
    async def test_update_post(
        self, db_session: Session, client: TestClient, app: FastAPI
    ):
        """Редактирование заметок"""

        current_user = await self._setup(db_session)

        async with db_session() as session:
            stmt = func.count(Post.id)
            count = await session.scalar(stmt)
            assert count == 0

        post = await create_post_service(
            async_session=db_session,
            create_post=CreatePostInRequest(
                title="getPost title",
                description="Test Post description",
            ),
            user_id=current_user.id,
        )

        url = app.url_path_for("update_post", post_id=post.id)
        post_date = {
            "title": "Update title",
            "description": "Update Post description",
        }
        response = client.patch(url, json=post_date)
        assert response.status_code == 401

        token = self._auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.patch(url, headers=headers, json=post_date)
        assert response.status_code == 200
        post_res = response.json()
        assert post_res["title"] == "Update title"

        async with db_session() as session:
            stmt = select(Post).where(Post.id == post.id)
            post_row = await session.scalar(stmt)
            assert post_row.title == "Update title"

        url = app.url_path_for("update_post", post_id=5)
        response = client.patch(url, headers=headers, json=post_date)
        assert response.status_code == 404

        # CRUD операции заметок допускаются только для личных заметок, проверка на 404
        user2 = await create_user_service(
            async_session=db_session,
            create_user=CreateUserInRequest(
                first_name="TestUserName2",
                last_name="TestLastName2",
                email="testuser2@example.com",
                password="123",
            ),
        )
        post2 = await create_post_service(
            async_session=db_session,
            create_post=CreatePostInRequest(
                title="getPost title 2",
                description="Test Post description 2",
            ),
            user_id=user2.id,
        )
        url = app.url_path_for("update_post", post_id=post2.id)
        response = client.get(url)
        assert response.status_code == 401

        token = self._auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.patch(url, headers=headers, json=post_date)
        assert response.status_code == 404

        await self._teardown(db_session)

    @pytest.mark.asyncio
    async def test_delete_post(
        self, db_session: Session, client: TestClient, app: FastAPI
    ):
        """Удаление заметок"""

        current_user = await self._setup(db_session)

        async with db_session() as session:
            stmt = func.count(Post.id)
            count = await session.scalar(stmt)
            assert count == 0

        post = await create_post_service(
            async_session=db_session,
            create_post=CreatePostInRequest(
                title="delete Post title",
                description="Test Post description",
            ),
            user_id=current_user.id,
        )

        url = app.url_path_for("delete_post", post_id=post.id)
        response = client.delete(url)
        assert response.status_code == 401

        token = self._auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(url, headers=headers)
        assert response.status_code == 200

        async with db_session() as session:
            stmt = func.count(Post.id)
            count = await session.scalar(stmt)
            assert count == 0

        url = app.url_path_for("delete_post", post_id=5)
        response = client.delete(url, headers=headers)
        assert response.status_code == 404

        # CRUD операции заметок допускаются только для личных заметок, проверка на 404
        user2 = await create_user_service(
            async_session=db_session,
            create_user=CreateUserInRequest(
                first_name="TestUserName2",
                last_name="TestLastName2",
                email="testuser2@example.com",
                password="123",
            ),
        )
        post2 = await create_post_service(
            async_session=db_session,
            create_post=CreatePostInRequest(
                title="getPost title 2",
                description="Test Post description 2",
            ),
            user_id=user2.id,
        )
        url = app.url_path_for("delete_post", post_id=post2.id)
        response = client.get(url)
        assert response.status_code == 401

        token = self._auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(url, headers=headers)
        assert response.status_code == 404

        await self._teardown(db_session)

    @pytest.mark.asyncio
    async def test_get_list_post(
        self, db_session: Session, client: TestClient, app: FastAPI
    ):
        """Просмотр заметок с пагинацией"""

        current_user = await self._setup(db_session)

        for i in range(10):
            await create_post_service(
                async_session=db_session,
                create_post=CreatePostInRequest(
                    title=f"Post{i} title",
                    description=f"Test Post{i} description",
                ),
                user_id=current_user.id,
            )

        async with db_session() as session:
            stmt = func.count(Post.id)
            count = await session.scalar(stmt)
            assert count == 10

        url = app.url_path_for("get_post_list")
        response = client.get(url)
        assert response.status_code == 401

        token = self._auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(url, headers=headers)
        assert response.status_code == 200
        result_list = response.json()
        assert result_list["total"] == 10
        assert result_list["posts"][0]["title"] == "Post0 title"
        assert len(result_list["posts"]) == 10

        # CRUD операции заметок допускаются только для личных заметок
        user2 = await create_user_service(
            async_session=db_session,
            create_user=CreateUserInRequest(
                first_name="TestUserName2",
                last_name="TestLastName2",
                email="testuser2@example.com",
                password="123",
            ),
        )
        await create_post_service(
            async_session=db_session,
            create_post=CreatePostInRequest(
                title="getPost title 2",
                description="Test Post description 2",
            ),
            user_id=user2.id,
        )
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(url, headers=headers)
        assert response.status_code == 200
        result_list = response.json()
        assert result_list["total"] == 10
        assert len(result_list["posts"]) == 10

        # постраничность
        response = client.get(url + "?limit=2&offset=0", headers=headers)
        assert response.status_code == 200
        result_list = response.json()
        assert result_list["total"] == 10
        assert len(result_list["posts"]) == 2
        assert result_list["posts"][0]["title"] == "Post0 title"

        response = client.get(url + "?limit=3&offset=2", headers=headers)
        assert response.status_code == 200
        result_list = response.json()
        assert result_list["total"] == 10
        assert len(result_list["posts"]) == 3
        assert result_list["posts"][0]["title"] == "Post2 title"

        await self._teardown(db_session)
