from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from backend.core.logger import logger
from backend.core.settings import settings
from backend.crud import get_actual_booking_token
from backend.schemas import BookEquipmentType

router = APIRouter(tags=["terminal"])


terminal_websocket = None
client_websocket = None


@router.websocket("/terminal/exporter")
async def terminal_endpoint(websocket: WebSocket, token: str = Query(...)):
    global terminal_websocket
    if token != settings.terminal_key:
        logger.error("Unauthorized access to terminal websocket")
        await websocket.close(4000)
        return

    await websocket.accept()
    terminal_websocket = websocket
    logger.info("Terminal connected")

    try:
        while True:
            data = await websocket.receive_text()
            if client_websocket:
                await client_websocket.send_text(data)
    except WebSocketDisconnect:
        logger.error("Terminal disconnected")
    finally:
        if terminal_websocket == websocket:
            terminal_websocket = None


@router.websocket("/terminal/client")
async def client_endpoint(websocket: WebSocket, token: str = Query(...)):
    global client_websocket
    await websocket.accept()
    if get_actual_booking_token(type=BookEquipmentType.raspberry_pi) != token:
        await websocket.close(code=4001)
        logger.info(f"Не авторизированный клиент, tokent {token}")
        return

    client_websocket = websocket
    logger.info("Client connected")

    try:
        if terminal_websocket:
            await terminal_websocket.send_text("\r")
        while True:
            data = await websocket.receive_text()
            if terminal_websocket:
                await terminal_websocket.send_text(data)
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    finally:
        if client_websocket == websocket:
            client_websocket = None
