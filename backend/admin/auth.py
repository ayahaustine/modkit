"""Admin authentication provider — restricts access to active superusers."""

import bcrypt
from sqlalchemy import select
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import LoginFailed

from core.database import AsyncSessionLocal
from modules.users.models import User

_SESSION_KEY_ID = "admin_user_id"
_SESSION_KEY_NAME = "admin_user_name"


class AdminAuthProvider(AuthProvider):
    """
    Authenticate admin users against the users table.

    Only accounts with is_superuser=True and is_active=True are granted access.
    Identity is persisted in a signed server-side session cookie managed by
    starlette's SessionMiddleware.
    """

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        """
        Validate credentials and write the user identity to the session.

        Args:
            username: Email address submitted via the login form.
            password: Plaintext password submitted via the login form.
            remember_me: Whether the user checked "remember me" (unused here).
            request: The incoming login request.
            response: The response object to attach session data to.

        Returns:
            The response object (starlette-admin redirects after this).

        Raises:
            LoginFailed: If credentials are wrong or the account lacks superuser rights.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(
                    User.email == username,
                    User.is_superuser == True,  # noqa: E712
                    User.is_active == True,  # noqa: E712
                )
            )
            user = result.scalar_one_or_none()

            if not user or not bcrypt.checkpw(
                password.encode(), user.hashed_password.encode()
            ):
                raise LoginFailed("Invalid credentials or insufficient permissions")

            request.session[_SESSION_KEY_ID] = str(user.id)
            request.session[_SESSION_KEY_NAME] = user.full_name or user.email

        return response

    async def is_authenticated(self, request: Request) -> bool:
        """Return True if a valid admin session exists."""
        return _SESSION_KEY_ID in request.session

    def get_admin_user(self, request: Request) -> AdminUser | None:
        """
        Return the AdminUser representation for the nav bar.

        Returns:
            AdminUser if a session exists, otherwise None.
        """
        if _SESSION_KEY_ID not in request.session:
            return None
        return AdminUser(username=request.session.get(_SESSION_KEY_NAME, "admin"))

    async def logout(self, request: Request, response: Response) -> Response:
        """Clear the admin session and return the response."""
        request.session.clear()
        return response
