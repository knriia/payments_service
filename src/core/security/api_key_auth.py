import secrets
from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Header, HTTPException, status

from core.config import Settings


def verify_api_key_value(x_api_key: str | None, settings: Settings) -> None:
    if x_api_key is None or not secrets.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


@inject
async def verify_api_key(
    settings: FromDishka[Settings],
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    verify_api_key_value(x_api_key=x_api_key, settings=settings)
