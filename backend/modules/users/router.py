from fastapi import APIRouter, Depends

from core.dependencies import CurrentUser
from modules.users.schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: CurrentUser) -> UserOut:
    return UserOut.model_validate(current_user)
