"""Admin package — starlette-admin mounted at /admin."""

from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin

from admin.auth import AdminAuthProvider
from admin.views import make_session_admin, make_user_admin
from core.config import settings
from core.database import engine


def create_admin() -> Admin:
    """
    Build and configure the starlette-admin instance.

    The admin is mounted separately from the FastAPI router tree so that
    its session middleware does not interfere with the main application.

    Returns:
        A configured Admin instance ready to be mounted via admin.mount_to(app).
    """
    admin = Admin(
        engine,
        title=f"{settings.APP_NAME} Admin",
        base_url="/admin",
        auth_provider=AdminAuthProvider(),
        middlewares=[
            Middleware(SessionMiddleware, secret_key=settings.JWT_SECRET_KEY),
        ],
    )

    admin.add_view(make_user_admin())
    admin.add_view(make_session_admin())

    return admin
