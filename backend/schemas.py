import uuid
from datetime import datetime, timedelta

from pydantic import (BaseModel, EmailStr, Field, field_validator,
                      model_validator)

from backend.enums import (BookEquipmentType, LangExecutionType, TaskType,
                           UserRoles)


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone_number: str | None = None
    role: UserRoles = UserRoles.USER


class TaskOut(BaseModel):
    id: str
    done: bool
    result_link: str | None
    type: TaskType
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    """Partitial without files request schema"""

    number: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType


class Task(BaseModel):
    number: str
    user_id: int
    flash_file: str
    # task_type: TaskType


class FpgaTask(Task):
    """FpgaTask represents a task from USER."""

    instruction_file: str
    execution_type: LangExecutionType = LangExecutionType.LITE


class ResultTask(BaseModel):
    """ResultTask represents a answer on user task"""

    number: str
    user_id: int
    link: str | None = None


class ResultTasksRequest(BaseModel):
    task_type: TaskType
    actual: bool = False


class BookingRequest(BaseModel):
    """BookingRequest represents a"""

    start_time: datetime
    end_time: datetime
    type: BookEquipmentType

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_hour_precision(cls, value: datetime) -> datetime:
        if value.minute != 0 or value.second != 0 or value.microsecond != 0:
            raise ValueError("Время должно быть ровно по часу, без минут и секунд")
        return value

    @model_validator(mode="after")
    def validate_duration(cls, values: "BookingRequest") -> "BookingRequest":
        if values.end_time - values.start_time != timedelta(hours=1):
            raise ValueError(
                "Разница между start_time и end_time должна быть ровно 1 час"
            )

        return values


class BookingResponse(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    type: BookEquipmentType
    active: bool


class BookingsAvailableRequest(BaseModel):
    type: BookEquipmentType


class AvailableSlots(BaseModel):
    slots: list[str]
    type: BookEquipmentType


class SessionToken(BaseModel):
    token: str


class FpgaSyncTask(BaseModel):
    """FpgaTask represents a task from user."""

    number: str
    flash_file: str | None = None
    instruction: str | None = None
