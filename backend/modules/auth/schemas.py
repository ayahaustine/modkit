from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    """
    Payload for the registration endpoint.
    contains:
    - email: User's email address (must be unique).
    - password: User's password (must be at least 8 characters).
    - full_name: Optional full name of the user.

    """

    email: EmailStr
    password: str
    full_name: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Enforce minimum password length of 8 characters."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    """
    Payload for the login endpoint.
    contains:
    - email: User's email address.
    - password: User's password.
    """

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Response body returned after a successful auth operation.
    contains:
    - message: Status message.
    """

    message: str = "ok"
