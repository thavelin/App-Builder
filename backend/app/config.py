"""
Configuration settings loaded from environment variables.
"""
from typing import List
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    openai_api_key: str = ""
    github_token: str = ""
    github_username: str = ""
    openai_model: str = "gpt-4-turbo-preview"  # Default to turbo for larger context
    jwt_secret_key: str = "your-secret-key-change-in-production-use-random-string"
    
    # CORS origins - stored as string, converted to list via property
    cors_origins_str: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")
    
    @field_validator("cors_origins_str", mode="before")
    @classmethod
    def parse_cors_origins_str(cls, v):
        """Handle CORS origins as string (comma-separated or empty)."""
        if v is None or v == "":
            return "http://localhost:3000"
        return str(v)
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if not self.cors_origins_str:
            return ["http://localhost:3000"]
        return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]


settings = Settings()

