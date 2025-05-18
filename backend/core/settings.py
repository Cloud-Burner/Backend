from typing import Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Cloud Burner API"
    version: str = "1.0.0"

    available_equipment: dict[str, Any] = {
        "fpga": ["DE10_lite", "green"],
        "micro": ["arduino_nano"],
        "terminal": ["raspberry_pi"],
    }

    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "admin"
    db_password: str = "admin"
    db_name: str = "burner"

    rabbit_host: str = "localhost"
    rabbit_port: int = 5672
    rabbit_user: str = "user"
    rabbit_password: str = "password"
    main_exchange: str = "main"
    result_queue: str = "result"

    s3_url: str = "http://localhost:9000"
    access_key: str = "f0Sxs0Bf2pqJDQtFNQZF"
    secret_key: str = "hrGuLOhzFZBNWtmL5TJ8wiB2e5d9jIHeSzdEYXbW"
    result_bucket: str = "result"
    task_bucket: str = "task"

    booking_max_days: int = 3

    # sync plates
    sync_fpga_queue: str = "sync_de10_lite_1"

    # preshared keys
    rpi_camera_key: str = "rpi"
    green_camera_key: str = "green"
    terminal_key: str = "terminal"

    docs_url: str = "/api/doc"
    openapi_url: str = "/api/openapi.json"

    host: str = "0.0.0.0"
    port: int = 8001
    reload: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
