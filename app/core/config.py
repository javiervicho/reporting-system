import os
from typing import List, Union, Optional
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Environmental Incident Reporting API"
    
    # CORS Configuration
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database Configuration
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    DATABASE_URI: Optional[str] = None
    
    @validator("DATABASE_URI", pre=True)
    def assemble_db_uri(cls, v: Optional[str], values: dict) -> str:
        if v:
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
    
    # Text Embedding Model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Default model for sentence transformers
    
    # Security Settings
    # Add security settings as needed (e.g., JWT secret, token expiration)
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Initialize settings
settings = Settings() 