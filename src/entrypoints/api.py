from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from entrypoints.container import create_container
from payments.presentation.payment_routes import payment_router


def create_app() -> FastAPI:
    app = FastAPI(title="Payment service")
    app.include_router(payment_router)
    container = create_container()
    setup_dishka(container, app)
    return app


app = create_app()
