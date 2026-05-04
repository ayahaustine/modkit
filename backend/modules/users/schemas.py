import uuid

from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    is_active: bool

    model_config = {"from_attributes": True}
