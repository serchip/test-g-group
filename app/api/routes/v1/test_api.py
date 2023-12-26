from fastapi import APIRouter

from app.api.dependencies.database import AsyncSession

router = APIRouter(prefix="/v1/test_api")


@router.get("/")
async def root():
    return {"message": "Hello World!"}


@router.get("/hello/{name}")
async def say_hello(name: str, session: AsyncSession):
    return {"message": f"Hello {name}"}
