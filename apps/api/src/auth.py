from fastapi import Header, HTTPException, status


def get_current_user(x_user_id: str | None = Header(default=None), x_user_email: str | None = Header(default=None)):
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing auth headers. Use x-user-id (MVP mode).",
        )
    return {"user_id": x_user_id, "email": x_user_email or f"{x_user_id}@local.test"}

