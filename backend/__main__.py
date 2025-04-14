from fastapi_offline import FastAPIOffline
from uvicorn import Config, Server

from backend.core.settings import settings
from backend.routes.authorization import router as auth_router

app = FastAPIOffline(
    title=settings.app_name,
    version=settings.version,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
    redoc_url=None,
)

app.include_router(auth_router)

if __name__ == "__main__":
    config = Config(
        app=app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info",
    )
    server = Server(config)
    server.run()
