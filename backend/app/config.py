"""
Configuration settings loaded from environment variables.
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_username: str = os.getenv("GITHUB_USERNAME", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    class Config:
        env_file = ".env"


settings = Settings()

