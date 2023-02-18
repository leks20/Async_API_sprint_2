import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str

    redis_host: str
    redis_port: int
    redis_expire_time: int

    elastic_schema: str
    elastic_host: str
    elastic_port: str

    log_level: str

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    class Config:
        env_file = "./.env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
