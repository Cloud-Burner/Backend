from fastapi_offline import FastAPIOffline
from uvicorn import Config, Server
from fastapi.middleware.cors import CORSMiddleware
from backend.core.settings import settings
from backend.routes.authorization import router as auth_router
from backend.routes.configuration import router as configuration_router
from backend.routes.result_consuming import router as rabbit_router
from backend.routes.task import router as task_router

# from faststream.rabbit.fastapi import RabbitRouter

app = FastAPIOffline(
    title=settings.app_name,
    version=settings.version,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
    redoc_url=None,
)

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(rabbit_router)
app.include_router(configuration_router)
ALLOWED_ORIGINS = [
    "https://client1.yourapp.com",
    "https://client2.yourapp.com",
    "http://localhost:5173", # локалка для тестов
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# @app.middleware("http")
# async def custom_cors_middleware(request: Request, call_next):
#     response = await call_next(request)
#     origin = request.headers.get("origin")
#     if origin in ALLOWED_ORIGINS:
#         response.headers["Access-Control-Allow-Origin"] = origin
#         response.headers["Access-Control-Allow-Credentials"] = "true"
#         response.headers["Access-Control-Allow-Methods"] = "*"
#         response.headers["Access-Control-Allow-Headers"] = "*"
#     return response

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
