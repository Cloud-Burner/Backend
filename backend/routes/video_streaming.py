from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from backend.core.logger import logger
from backend.core.settings import settings
from backend.crud import get_actual_booking_token
from backend.enums import BookEquipmentType

# from starlette.websockets import WebSocketDisconnect


camera_clients = {BookEquipmentType.raspberry_pi: [], BookEquipmentType.green: []}
router = APIRouter()


@router.websocket("/camera/exporter")
async def camera_stream_from_pc2(
    websocket: WebSocket, type: BookEquipmentType = Query(...), token: str = Query(...)
) -> None:
    if token not in [settings.rpi_camera_key, settings.green_camera_key]:
        await websocket.close(code=4000)
        logger.error("Not authorized exporter")
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            for client in camera_clients[type]:
                await client.send_bytes(data)
    except WebSocketDisconnect:
        logger.info(f"Exporter {BookEquipmentType} disconnected")
    except Exception as e:
        print("Ошибка потока:", e)


@router.websocket("/camera/viewer")
async def stream_to_client(
    websocket: WebSocket, type: BookEquipmentType = Query(...), token: str = Query(...)
):
    if get_actual_booking_token(type=type) != token:
        await websocket.close(code=4000)
        logger.info("Client disconnected 401")
        return
    await websocket.accept()
    camera_clients[type].append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        camera_clients[type].remove(websocket)
