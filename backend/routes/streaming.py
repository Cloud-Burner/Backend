import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.core.settings import settings

router = APIRouter(tags=["streaming"])


@router.post("/webrtc/offer")
async def forward_offer(request: Request):
    offer_data = await request.json()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.stream_export_address}/offer", json=offer_data
            )
            response.raise_for_status()
            return JSONResponse(content=response.json())
    except httpx.HTTPError as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
