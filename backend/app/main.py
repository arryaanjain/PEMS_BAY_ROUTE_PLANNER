from fastapi import FastAPI
from .routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="Sample FastAPI MySQL App")
    app.include_router(router, prefix="/api")
    return app


app = create_app()
