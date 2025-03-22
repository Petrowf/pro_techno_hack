from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str
    API_V1_STR: str 
    FCM_API_KEY: str  # Добавьте это поле
    FCM_SERVICE_ACCOUNT : str
    DB_USER : str
    DB_PASSWORD : str
    DB_NAME : str
    DB_HOST : str
    DB_PORT : str
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()