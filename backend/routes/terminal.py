import asyncio

import websockets
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.settings import settings

router = APIRouter(tags=["terminal"])


@router.websocket("/terminal/ws")
async def terminal_proxy(websocket: WebSocket):
    await websocket.accept()
    try:
        async with websockets.connect(settings.terminal_export_address) as agent_ws:

            async def user_to_agent():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await agent_ws.send(data)
                except WebSocketDisconnect:
                    await agent_ws.close()

            async def agent_to_user():
                try:
                    async for message in agent_ws:
                        await websocket.send_text(message)
                except Exception:
                    await websocket.close()

            async def close_after_timeout():
                await asyncio.sleep(3600)
                await websocket.close(code=1000, reason="Session timeout")
                await agent_ws.close()

            await asyncio.gather(
                user_to_agent(), agent_to_user(), close_after_timeout()
            )

    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
