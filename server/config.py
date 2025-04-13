from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str
    google_client_id: str
    google_client_secret: str
    database_url: str
    auth_url: str
    token_url: str
    auth_provider_cert_url: str
    redirect_urls: str
    admin_email: str

    class Config:
        env_file = ".env"


settings = Settings()
