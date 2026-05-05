"""Admin ModelView definitions for each domain model."""

from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView

from modules.auth.models import Session
from modules.users.models import User


class UserAdmin(ModelView):
    """
    Admin view for the User model.

    hashed_password is intentionally excluded from all views.
    Password management should be done via the API or create_superuser script.
    """

    # Explicit field list keeps hashed_password out of every view.
    fields = [
        "id",
        "email",
        "full_name",
        "is_active",
        "is_superuser",
        "created_at",
        "updated_at",
    ]

    # id and timestamps are managed by the DB.
    exclude_fields_from_create = ["id", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]

    searchable_fields = ["email", "full_name"]
    sortable_fields = ["email", "is_active", "is_superuser", "created_at"]


class SessionAdmin(ModelView):
    """
    Read-only admin view for active refresh-token sessions.

    Create and edit are disabled — sessions are managed exclusively via
    the auth API (login / refresh / logout).
    """

    fields = [
        "id",
        "user_id",
        "expires_at",
        "user_agent",
        "ip_address",
        "created_at",
    ]

    sortable_fields = ["expires_at", "created_at"]

    def can_create(self, request: Request) -> bool:
        """Disable session creation from the admin UI."""
        return False

    def can_edit(self, request: Request) -> bool:
        """Disable session editing from the admin UI."""
        return False


def make_user_admin() -> UserAdmin:
    """Instantiate UserAdmin bound to the User model."""
    return UserAdmin(User, label="Users", icon="fa fa-users")


def make_session_admin() -> SessionAdmin:
    """Instantiate SessionAdmin bound to the Session model."""
    return SessionAdmin(Session, label="Sessions", icon="fa fa-key")
