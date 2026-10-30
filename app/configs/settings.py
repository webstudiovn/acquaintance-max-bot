from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

class Max(BaseModel):
    token: str

class Yoomoney(BaseModel):
    token: str
    receiver: int

class Database(BaseModel):
    name: str
    host: str
    port: int
    user: str
    password: str

class Settings(BaseSettings):
    max: Max
    db: Database
    yoomoney: Yoomoney  # <-- добавляем вложенную конфигурацию

    model_config = {
        "env_prefix": "",
        "case_sensitive": False,
        "env_nested_delimiter": "__",
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

settings = Settings()