from functools import wraps
from typing import AsyncGenerator
from typing import Any
import jwt
import httpx
from httpx import AsyncClient
from fastapi import HTTPException
from fastapi import status
from core.logger import logger
from core.config import settings


async def get_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient() as client:
        yield client


async def verify_token(
    access_token: str, required_roles: list[str]
) -> str | None:
    
    client = AsyncClient()

    try:
        response = await client.get(
            url=settings.verify_token_url,
            headers={
                "Authorization": f"Bearer {access_token}",
            }
        )
        response.raise_for_status()

    except httpx.HTTPStatusError as e:
        logger.error(e, exc_info=True)
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e,
        )

    decoded_token = jwt.decode(access_token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    role = decoded_token["sub"]["role"]

    if role in required_roles:
        return None

    return None


def check_permission(required_roles: list[str]) -> Any:
    def outer_wrapper(function: Any) -> Any:
        @wraps(function)
        async def inner_wrapper(*args: Any, **kwargs: Any) -> Any:

            access_token = kwargs.get("HTTPBearer")

            if not access_token:
                msg = "Missing authorization token"
                logger.error(msg, exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=msg,
                )

            result = await verify_token(access_token, required_roles)

            if isinstance(result, str):
                logger.error(result, exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=result,
                )
            return await function(*args, **kwargs)

        return inner_wrapper

    return outer_wrapper
