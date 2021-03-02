import os
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseSettings

secret_key = os.getenv("SECRET_KEY") if os.getenv("SECRET_KEY") else "abc"
db_host = os.getenv("DB_HOST") if os.getenv("DB_HOST") else "localhost"

class Settings(BaseSettings):
    SECRET_KEY = secret_key
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:password@{db_host}/fastapi"
    SQLALCHEMY_DATABASE_SSL = False
    SQLALCHEMY_DATABASE_MIN_POOL = 1
    SQLALCHEMY_DATABASE_MAX_POOL = 20

settings = Settings()
