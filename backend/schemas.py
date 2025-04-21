import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from backend.enums import LangExecutionType, TaskType, UserRoles


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
