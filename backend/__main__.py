import time
from datetime import datetime, timedelta
from threading import Thread

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_offline import FastAPIOffline
from loguru import logger
from sqlalchemy.orm import Session
from uvicorn import Config, Server

from backend.core.db import get_db
from backend.core.settings import settings
from backend.models import Task
from backend.routes.authorization import router as auth_router
from backend.routes.booking import router as booking_router
from backend.routes.configuration import router as configuration_router
from backend.routes.result_consuming import router as rabbit_router
from backend.routes.sync_fpga_task import router as sync_fpga_router
from backend.routes.task import router as task_router
from backend.routes.terminal import router as terminal_router
from backend.routes.video_streaming import router as streaming_router

# from backend.core.logger import setup_logger


app = FastAPIOffline(
    title=settings.app_name,
    version=settings.version,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
    redoc_url=None,
)
UPLOAD_DIR = "./static/hls"
app.include_router(auth_router)
app.include_router(task_router)
app.include_router(rabbit_router)
app.include_router(configuration_router)
app.include_router(booking_router)
app.include_router(terminal_router)
app.include_router(streaming_router)
app.include_router(sync_fpga_router)

def task_timeout_watcher():
    while True:
        try:
            db: Session = next(get_db())
            timeout_time = datetime.utcnow() - timedelta(minutes=5)

            tasks_to_update = (
                db.query(Task)
                .filter(Task.done == False)
                .filter(Task.created_at < timeout_time)
                .all()
            )

            for task in tasks_to_update:
                task.done = True
                task.result_link = "timeout"

            if tasks_to_update:
                db.commit()
                logger.info(f"[scheduler] Отметили {len(tasks_to_update)} просроченных задач")

        except Exception as e:
            logger.error(f"[scheduler] Ошибка: {e}")
        finally:
            db.close()

        time.sleep(60)  # Ждать 1 минуту
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def start_timeout_scheduler():
    t = Thread(target=task_timeout_watcher, daemon=True)
    t.start()

if __name__ == "__main__":
    # setup_logger()
    config = Config(
        app=app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info",
        # log_config=None
    )
    server = Server(config)
    server.run()
