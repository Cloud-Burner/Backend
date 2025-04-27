from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from backend.enums import BookEquipmentType, TaskType, UserRoles


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str]
    last_name: Mapped[str]

    email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_number: Mapped[str | None] = mapped_column(nullable=True)

    hashed_password: Mapped[str] = mapped_column(String(256))
    role: Mapped[UserRoles] = mapped_column(default=UserRoles.USER)

    avatar_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    result_link: Mapped[str] = mapped_column(String(), nullable=True)
    type: Mapped[TaskType]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="tasks")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="bookings")

    start_time: Mapped[datetime] = mapped_column(index=True)
    end_time: Mapped[datetime] = mapped_column(index=True)
    session_token: Mapped[str] = mapped_column(index=True)

    type: Mapped[BookEquipmentType]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
