"""
CLI script to create the first superuser.

Usage:
    uv run python scripts/create_superuser.py

Inside Docker:
    docker exec -it modkit-backend-1 python scripts/create_superuser.py
"""

import asyncio
import getpass
import sys

from sqlalchemy import select

from core.database import AsyncSessionLocal
from modules.users.models import User


async def _create_superuser(email: str, password: str, full_name: str | None) -> None:
    """
    Insert a new superuser or promote an existing account.

    Args:
        email: Email address for the superuser account.
        password: Plaintext password (will be hashed before storage).
        full_name: Optional display name.
    """
    import bcrypt

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            user.hashed_password = hashed
            user.is_superuser = True
            user.is_active = True
            print(f"Updated existing user '{email}' to superuser.")
        else:
            user = User(
                email=email,
                hashed_password=hashed,
                full_name=full_name,
                is_superuser=True,
                is_active=True,
            )
            session.add(user)
            print(f"Created superuser '{email}'.")

        await session.commit()


def main() -> None:
    """
    Prompt for superuser credentials and create the account.
    """
    print("Create ModKit superuser")
    print("-" * 30)

    email = input("Email: ").strip()
    if not email:
        print("Error: email is required.", file=sys.stderr)
        sys.exit(1)

    full_name = input("Full name (optional): ").strip() or None

    password = getpass.getpass("Password: ")
    if len(password) < 8:
        print("Error: password must be at least 8 characters.", file=sys.stderr)
        sys.exit(1)

    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Error: passwords do not match.", file=sys.stderr)
        sys.exit(1)

    asyncio.run(_create_superuser(email, password, full_name))


if __name__ == "__main__":
    main()
