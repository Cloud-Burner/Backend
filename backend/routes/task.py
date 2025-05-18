import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from faststream.rabbit import RabbitExchange
from sqlalchemy.orm import Session

from backend import schemas
from backend.core.db import get_db
from backend.core.settings import settings
from backend.enums import TaskType
from backend.models import Task, User
from backend.routes.authorization import oauth2_scheme
from backend.routes.result_consuming import router as rabbit_router
from backend.utils import auth as auth_utils
from backend.utils import s3

router = APIRouter(prefix="/task", tags=["tasks"])

main_exchange = RabbitExchange(name=settings.main_exchange)


@router.get("s")
async def get_task(
    task_type: schemas.TaskType | None = Query(default=None),
    done: bool = False,
    all_tasks: bool = False,
    limit: int = Query(default=100),
    offset: int = Query(default=0),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> list[schemas.TaskOut]:
    user_id = int(auth_utils.decode_access_token(token).get("sub"))
    query = (
        db.query(Task).order_by(Task.created_at.desc()).filter(Task.user_id == user_id)
    )
    if not all_tasks:
        query = query.filter(Task.done == done, Task.type == task_type)
    return query.offset(offset).limit(limit).all()


@router.post("/fpga")
async def create_task_fpga(
    task_type: schemas.TaskType = Form(...),
    flash_file: UploadFile = File(...),
    instruction_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    user_id = int(auth_utils.decode_access_token(token).get("sub"))
    if Path(flash_file.filename).suffix.lower() != ".svf":
        raise HTTPException(
            status_code=400, detail="Разрешены только svf файлы, в качестве прошивки"
        )
    if Path(instruction_file.filename).suffix.lower() != ".txt":
        raise HTTPException(
            status_code=400, detail="Разрешены только txt файлы в качестве инструкции"
        )

    existing = (
        db.query(Task)
        .join(Task.user)
        .filter(User.id == user_id, Task.type == task_type, Task.done.is_(False))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409, detail="У вас уже есть незавершённая задача этого типа."
        )
    task_number = str(uuid.uuid4())
    flash: bytes = await flash_file.read()
    instruction: bytes = await instruction_file.read()
    flash_file_name = f"{user_id}_{task_number}.svf"
    instruction_file_name = f"{user_id}_{task_number}.txt"
    await s3.upload_bytes(bucket=settings.task_bucket, file=flash, name=flash_file_name)
    await s3.upload_bytes(
        bucket=settings.task_bucket, file=instruction, name=instruction_file_name
    )

    await rabbit_router.broker.publish(
        message=schemas.FpgaTask(
            number=task_number,
            user_id=user_id,
            flash_file=flash_file_name,
            instruction_file=instruction_file_name,
        ),
        headers={"board": task_type},
        exchange=main_exchange,
    )
    task = Task(
        id=task_number,
        user_id=user_id,
        type=task_type,
        done=False,
        created_at=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.post("/micro")
async def create_task_micro(
    flash_file: UploadFile = File(...),
    instruction_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    user_id = int(auth_utils.decode_access_token(token).get("sub"))
    if Path(flash_file.filename).suffix.lower() != ".hex":
        raise HTTPException(
            status_code=400, detail="Разрешены только hex    файлы, в качестве прошивки"
        )
    if Path(instruction_file.filename).suffix.lower() != ".txt":
        raise HTTPException(
            status_code=400, detail="Разрешены только txt файлы в качестве инструкции"
        )

    existing = (
        db.query(Task)
        .join(Task.user)
        .filter(
            User.id == user_id, Task.type == TaskType.ARDUINO_NANO, Task.done.is_(False)
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409, detail="У вас уже есть незавершённая задача этого типа."
        )
    task_number = str(uuid.uuid4())
    flash: bytes = await flash_file.read()
    instruction: bytes = await instruction_file.read()
    flash_file_name = f"{user_id}_{task_number}.hex"
    instruction_file_name = f"{user_id}_{task_number}.txt"
    await s3.upload_bytes(bucket=settings.task_bucket, file=flash, name=flash_file_name)
    await s3.upload_bytes(
        bucket=settings.task_bucket, file=instruction, name=instruction_file_name
    )

    await rabbit_router.broker.publish(
        message=schemas.FpgaTask(
            number=task_number,
            user_id=user_id,
            flash_file=flash_file_name,
            instruction_file=instruction_file_name,
        ),
        headers={"board": TaskType.ARDUINO_NANO},
        exchange=main_exchange,
    )
    task = Task(
        id=task_number,
        user_id=user_id,
        type=TaskType.ARDUINO_NANO,
        done=False,
        created_at=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
