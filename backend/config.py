from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    pg_dsn: PostgresDsn
    postgres_user: str
    postgres_password: str
    postgres_db: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


settings = Settings()  # type: ignore - issue with pylance, waiting for fix on github
