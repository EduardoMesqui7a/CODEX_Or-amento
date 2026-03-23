from fastapi import APIRouter, Depends

from ..auth import get_current_user
from ..schemas import SessionVerifyResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/session/verify", response_model=SessionVerifyResponse)
def verify_session(user=Depends(get_current_user)):
    return SessionVerifyResponse(user_id=user["user_id"], email=user["email"], authenticated=True)

