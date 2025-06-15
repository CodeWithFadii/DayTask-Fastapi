from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expires_days: int
    smtp_password: str
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
