from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "forecastly"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8000"]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # 쉼표로 구분된 문자열을 리스트로 변환
            if not v.strip():
                return ["http://localhost:3000", "http://localhost:8000"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # LLM (OpenRouter)
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini"  # 기본 모델
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

