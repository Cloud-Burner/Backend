import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from faststream.rabbit import RabbitQueue

from backend.core.logger import logger
from backend.core.settings import settings
from backend.crud import get_actual_booking_token
from backend.enums import PinStates
from backend.routes.result_consuming import router as rabbit_router
from backend.schemas import BookEquipmentType, FpgaSyncTask
from backend.utils import s3

pin_button_mapper = {1: 24, 2: 23, 3: 25, 4: 15, 5: 18, 6: 1, 7: 8, 8: 7}

router = APIRouter(prefix="/sync/fpga", tags=["sync_fpga"])

queue = RabbitQueue(name=settings.sync_fpga_queue, durable=True)


@router.post("/flash")
async def sync_fpga_flash(token: str, flash_file: UploadFile = File(...)):
    if get_actual_booking_token(type=BookEquipmentType.green) != token:
        return HTTPException(status_code=401, detail="У вас нет активной сессии")
    if Path(flash_file.filename).suffix.lower() != ".svf":
        raise HTTPException(
            status_code=400, detail="Разрешены только svf файлы, в качестве прошивки"
        )

    task_number = str(uuid.uuid4())
    flash: bytes = await flash_file.read()
    flash_file_name = f"sync_{task_number}.svf"
    await s3.upload_bytes(bucket=settings.task_bucket, file=flash, name=flash_file_name)

    await rabbit_router.broker.publish(
        message=FpgaSyncTask(flash_file=flash_file_name, number=task_number),
        queue=queue,
    )
    logger.info("Sync flash task sent to MQ")


@router.post("/command")
async def sync_fpga_command(token: str, pin: int, state: PinStates):
    if get_actual_booking_token(type=BookEquipmentType.green) != token:
        return HTTPException(status_code=401, detail="У вас нет активной сессии")
    task_number = str(uuid.uuid4())
    await rabbit_router.broker.publish(
        message=FpgaSyncTask(
            number=task_number,
            instruction=f"pin {pin_button_mapper.get(pin, 1)} {state.value}",
        ),
        queue=queue,
    )
    logger.info("Sync command task sent to MQ")
