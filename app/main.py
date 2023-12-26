from fastapi import FastAPI

from app.api.api import router as api_router
from app.core.config import settings


def get_application() -> FastAPI:
    application = FastAPI(
        debug=settings.DEBUG,
    )

    application.include_router(api_router)

    return application


app = get_application()
