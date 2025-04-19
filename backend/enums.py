"""This module contains the local enums."""

from enum import StrEnum


class UserRoles(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


class LangExecutionType(StrEnum):
    """Enumeration of lang types"""

    HARD = "hard"
    OPTIMIZED = "optimized"
    LITE = "lite"


class TaskType(StrEnum):
    DE10_LITE = "DE10_lite"
    GREEN = "green"
    ARDUINO_NANO = "arduino_nano"
