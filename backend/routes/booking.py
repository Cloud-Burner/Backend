import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from backend import schemas
from backend.core.db import get_db
from backend.enums import BookEquipmentType
from backend.models import Booking
from backend.routes.authorization import oauth2_scheme
from backend.utils import auth as auth_utils

router = APIRouter(prefix="/booking", tags=["booking"])


@router.post("")
async def create_booking(
    booking_in: schemas.BookingRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> schemas.BookingRequest:
    user_id = int(auth_utils.decode_access_token(token).get("sub"))
    query = select(Booking).where(
        and_(
            Booking.user_id == user_id,
            Booking.type == booking_in.type,
            Booking.end_time > datetime.now(),
        )
    )

    if db.execute(query).scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="У вас уже есть активная бронь этого типа"
        )

    booking = Booking(
        user_id=user_id,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time,
        type=booking_in.type,
        session_token=str(uuid.uuid4()),
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get(
    "s",
)
async def get_my_bookings(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    equipment_type: BookEquipmentType | None = None,
    only_actual: bool = False,
) -> list[schemas.BookingResponse]:
    user_id = int(auth_utils.decode_access_token(token).get("sub"))
    query = (
        select(Booking)
        .where(Booking.user_id == user_id)
        .order_by(Booking.start_time.desc())
    )
    query = query.filter(Booking.type == equipment_type) if equipment_type else query
    query = query.filter(Booking.end_time > datetime.now()) if only_actual else query
    bookings = db.scalars(query)
    now = datetime.now()
    ans = [
        schemas.BookingResponse(
            id=b.id,
            start_time=b.start_time,
            end_time=b.end_time,
            type=b.type,
            active=True if b.start_time < now and b.end_time > now else False,
        )
        for b in bookings
    ]

    return ans


@router.delete("")
async def delete_booking(
    booking_id: int = Query(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    user_id = int(auth_utils.decode_access_token(token).get("sub"))
    query = select(Booking).where(
        and_(
            Booking.id == booking_id,
            Booking.user_id == user_id,
            Booking.end_time > datetime.utcnow(),
        )
    )
    booking = db.execute(query).scalar_one_or_none()
    if not booking:
        raise HTTPException(
            status_code=404, detail="Бронь не найдена или уже завершена"
        )

    db.delete(booking)
    db.commit()
    return Response(status_code=204)


@router.get("s/available", response_model=schemas.AvailableSlots)
async def get_available_hours(
    type: BookEquipmentType = Query(...),
    db: Session = Depends(get_db),
):
    """
    Получить список доступных часовых интервалов между start_date и end_date для заданного типа устройства
    """
    start_date: datetime = datetime.now()
    end_date: datetime = datetime.now() + timedelta(days=2)
    query = select(Booking).where(
        and_(
            Booking.type == type,
            Booking.end_time > start_date,
            Booking.start_time < end_date,
        )
    )
    busy_bookings = db.scalars(query).all()

    available_slots = []
    current = start_date.replace(minute=0, second=0, microsecond=0)
    while current < end_date:
        next_hour = current + timedelta(hours=1)
        overlapping = any(
            booking.start_time < next_hour and booking.end_time > current
            for booking in busy_bookings
        )
        if not overlapping:
            available_slots.append(current.strftime("%Y-%m-%d %H:%M"))
        current = next_hour

    return schemas.AvailableSlots(slots=available_slots, type=type)


@router.get("/session_token")
async def get_session_token(
    booking_id: int = Query(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> schemas.SessionToken:
    user_id = int(auth_utils.decode_access_token(token).get("sub"))
    now = datetime.now()
    query = select(Booking).where(
        Booking.id == booking_id,
        Booking.user_id == user_id,
        Booking.start_time < now,
        Booking.end_time > now,
    )
    booking = db.execute(query).scalar_one_or_none()
    if not booking:
        raise HTTPException(401, detail="У вас нет активной брони")
    return schemas.SessionToken(token=booking.session_token)


@router.get("")
async def get_booking_by_token(
    token: str = Query(...),
    type: BookEquipmentType = Query(...),
    db: Session = Depends(get_db),
):
    query = select(Booking).where(Booking.session_token == token, Booking.type == type)
    booking = db.execute(query).scalar_one_or_none()
    if not booking:
        return HTTPException(401, detail="You have no booking with this token")
    return booking
