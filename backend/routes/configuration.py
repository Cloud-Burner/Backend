from fastapi import APIRouter

from backend.core.settings import settings

router = APIRouter(prefix="/configuration", tags=["configuration"])


@router.get("")
async def get_configuration():
    return settings.available_equipment
