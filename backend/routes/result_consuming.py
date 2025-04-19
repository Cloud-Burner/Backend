from faststream.rabbit import RabbitQueue
from faststream.rabbit.fastapi import RabbitMessage, RabbitRouter

from backend.core.db import get_db
from backend.core.settings import settings
from backend.models import Task
from backend.schemas import ResultTask

router = RabbitRouter(
    url=f"amqp://{settings.rabbit_user}:{settings.rabbit_password}@{settings.rabbit_host}:{settings.rabbit_port}/"
)

result_exchange = RabbitQueue(name=settings.result_queue, durable=True)


@router.broker.subscriber(queue=result_exchange)
async def result_callback(result: RabbitMessage):
    result = ResultTask(**await result.decode())
    db = next(get_db())
    task = db.query(Task).filter(Task.id == result.number).first()
    task.result_link = result.link
    task.done = True
    db.commit()
