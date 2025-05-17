from datetime import datetime

from sqlalchemy import select

from backend.core.db import get_db
from backend.enums import BookEquipmentType
from backend.models import Booking


def get_actual_booking_token(type: BookEquipmentType):
    db = next(get_db())
    now = datetime.now()
    query = select(Booking).where(
        Booking.type == type, Booking.start_time < now, Booking.end_time > now
    )
    booking = db.execute(query).scalar_one_or_none()
    db.close()
    return booking.session_token if booking else None
