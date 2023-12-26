import asyncio

from app.db.database import AsyncSessionLocal
from app.schemas.request.user import CreateUserInRequest
from app.services.user import create_user_service


async def create_user(body: CreateUserInRequest):
    pg_session = AsyncSessionLocal
    return await create_user_service(async_session=pg_session, create_user=body)


if __name__ == "__main__":
    asyncio.run(
        create_user(
            CreateUserInRequest(
                first_name="TestUserName",
                last_name="TestLastName",
                email="testuser@example.com",
            )
        )
    )
