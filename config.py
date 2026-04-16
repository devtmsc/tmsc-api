from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool
    MASTER_DATABASE_URL: str
    REPLICATE_DATABASE_URL: str
    DATABASE_SEARCH_PATH: str
    USER_MODEL_PATH: str
    SECRET_KEY: str
    ALGORITHM: str
    BASE_DIR: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    JWT_SECRET_KEY: str
    RATELIMITING: str
    REDIS_MASTER: str
    REDIS_CLIENT: str
    DATABASE_SEARCH_PATH_CATEGORY: str
    DATABASE_SEARCH_PATH_LOGS: str
    DATABASE_SEARCH_PATH_CUSTOMER: str
    IMAGE_DIRECTORY: str
    FILE_DIRECTORY: str
    
    AWS_ENDPOINT: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET: str
    AWS_ROOT: str
    MEDIA_URL: str
    
    GEMINI_API_KEY: str
    API_KEY_NAME: str
    API_KEY: str

    class Config:
        env_file = "app/.env"


settings = Settings()
