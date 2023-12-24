from pydantic_settings import BaseSettings
from pydantic import EmailStr


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_username: str
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    sender_email: EmailStr
    domain: str
    base_url: str
    google_client_id: str
    google_client_secret: str
    google_redirect_uri:str

    class Config:
        env_file = ".env"


settings = Settings()
