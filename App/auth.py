from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import NOXIS_API_KEYS

_bearer = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> str | None:
    if not NOXIS_API_KEYS:
        return None
    if credentials is None or credentials.credentials not in NOXIS_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Invalid or missing API key",
                    "type": "authentication_error",
                    "code": "INVALID_API_KEY",
                }
            },
        )
    return credentials.credentials
