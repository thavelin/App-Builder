"""
Configuration settings loaded from environment variables.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_username: str = os.getenv("GITHUB_USERNAME", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-use-random-string")
    
    # CORS origins - split comma-separated string into list
    cors_origins: List[str] = [
        origin.strip() 
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    
    class Config:
        env_file = ".env"


settings = Settings()

