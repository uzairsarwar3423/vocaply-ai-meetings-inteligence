from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Vocaply AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ENCRYPTION_KEY: Optional[str] = None # For encrypting OAuth tokens
    
    # DATABASE
    DATABASE_URL: str
    REDIS_URL: str

    # CELERY (defaults to Redis if not explicitly set)
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @validator("CELERY_BROKER_URL", pre=True, always=True)
    def set_celery_broker(cls, v, values):
        return v or values.get("REDIS_URL", "redis://localhost:6379/0")

    @validator("CELERY_RESULT_BACKEND", pre=True, always=True)
    def set_celery_backend(cls, v, values):
        return v or values.get("REDIS_URL", "redis://localhost:6379/0")
    
    # SUPABASE
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # B2 (Backblaze)
    B2_KEY_ID: Optional[str] = None
    B2_APPLICATION_KEY: Optional[str] = None
    B2_BUCKET_NAME: Optional[str] = None

    # OPENAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_RETRIES: int = 3
    OPENAI_MONTHLY_BUDGET_USD: float = 50.0
    
    # ZOOM OAUTH
    ZOOM_CLIENT_ID: Optional[str] = None
    ZOOM_CLIENT_SECRET: Optional[str] = None
    ZOOM_REDIRECT_URI: Optional[str] = None
    ZOOM_WEBHOOK_SECRET: Optional[str] = None
    
    # GOOGLE OAUTH
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    GOOGLE_AUTH_REDIRECT_URI: Optional[str] = "http://localhost:3000/auth/callback/google"

    # SENDGRID (Day 26: Email notifications)
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@vocaply.ai"

    # SLACK (Day 26: Slack notifications — stub when not configured)
    SLACK_BOT_TOKEN: Optional[str] = None

    # FRONTEND (used in email CTA links)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
