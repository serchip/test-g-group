from fastapi import APIRouter

# from .routes.v1 import test_api as test_api_v1
from .routes.v1 import auth as auth_v1
from .routes.v1 import post as post_v1
from .routes.v1 import user as user_v1

router = APIRouter(prefix="/api")

# router.include_router(test_api_v1.router, tags=['test_api'])
router.include_router(user_v1.router, tags=["user"])
router.include_router(auth_v1.router, tags=["auth"])
router.include_router(post_v1.router, tags=["post"])
