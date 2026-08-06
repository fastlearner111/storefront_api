from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Make individual fields optional with sensible defaults for local dev
    database_hostname: Optional[str] = "localhost"
    database_port: Optional[str] = "5432"
    database_password: Optional[str] = "postgres"
    database_name: Optional[str] = "postgres"
    database_username: Optional[str] = "postgres"

    # Full URL field for Heroku
    database_url: Optional[str] = None

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    def get_database_url(self) -> str:
        # 1. If Heroku's DATABASE_URL is present, use it and fix the driver prefix
        if self.database_url:
            url = self.database_url
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql://", 1)
            return url
        
        # 2. Fallback to individual components (Local Dev)
        return (
            f"postgresql://{self.database_username}:"
            f"{self.database_password}@{self.database_hostname}:"
            f"{self.database_port}/{self.database_name}"
        )


    @property
    def DATABASE_URL(self) -> str:
        return self.get_database_url()

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()