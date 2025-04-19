# @router.get("/calendar/available", response_model=List[datetime])
# def get_available_hours(db: Session = Depends(...)):
#     now = datetime.utcnow()
#     window_end = now + timedelta(days=2)
#
#     # Все часы, на которые уже есть бронь
#     booked_hours = db.query(Booking.start_time).filter(
#         Booking.start_time >= now,
#         Booking.start_time <= window_end
#     ).all()
#
#     booked_set = {b[0] for b in booked_hours}
#
#     # Генерируем все слоты на 2 дня вперёд, по часу
#     all_hours = [now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=i)
#                  for i in range(2 * 24)]
#
#     available = [slot for slot in all_hours if slot not in booked_set]
#
#     return available
