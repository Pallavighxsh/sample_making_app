import os
from fastapi import HTTPException, status

# Later move this to Render env vars
ACCESS_PASSWORD = os.getenv("PHI_APP_PASSWORD", "Savvy?")

def verify_password(password: str):
    if password != ACCESS_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access credentials"
        )
