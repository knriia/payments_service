from collections.abc import AsyncIterable

import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from core.config import Settings
from core.security.api_key_auth import verify_api_key


class SettingsTestProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings(
            DB_HOST="localhost",
            DB_PORT="5432",
            DB_NAME="test",
            DB_USER="test",
            DB_PASSWORD="test",  # noqa: S106
            RABBIT_USER="guest",
            RABBIT_PASS="guest",  # noqa: S106
            API_KEY="test-api-key",
        )


@pytest_asyncio.fixture
async def client() -> AsyncIterable[AsyncClient]:
    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(verify_api_key)])
    async def protected() -> dict[str, str]:
        return {"status": "ok"}

    container = make_async_container(SettingsTestProvider())
    setup_dishka(container, app)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client

    await container.close()


@pytest.mark.asyncio
async def test_request_with_valid_api_key_passes(client: AsyncClient) -> None:
    response = await client.get("/protected", headers={"X-API-Key": "test-api-key"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_request_without_api_key_returns_401(client: AsyncClient) -> None:
    response = await client.get("/protected")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key"}


@pytest.mark.asyncio
async def test_request_with_invalid_api_key_returns_401(client: AsyncClient) -> None:
    response = await client.get("/protected", headers={"X-API-Key": "wrong-key"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key"}
