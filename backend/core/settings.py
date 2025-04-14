from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Terminal Access API"
    version: str = "1.0.0"

    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "admin"
    db_password: str = "admin"
    db_name: str = "burner"

    jwt_secret: str = "supersecret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    docs_url: str = "/api/doc"
    openapi_url: str = "/api/openapi.json"

    host: str = "localhost"
    port: int = 8001
    reload: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
