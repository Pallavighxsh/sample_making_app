import os
from fastapi import HTTPException, status

APP_PASSWORD = os.getenv("PHI_APP_PASSWORD", "xxxx")


def verify_password(password: str) -> None:
    if password != APP_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password.",
        )
