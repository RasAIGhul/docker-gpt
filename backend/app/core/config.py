import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DockerGPT"
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Docker Hub settings
    DOCKER_HUB_USERNAME: str = os.getenv("DOCKER_HUB_USERNAME", "")
    DOCKER_HUB_PASSWORD: str = os.getenv("DOCKER_HUB_PASSWORD", "")
    
    # Logging
    LOG_FILE: str = "dockergpt.log"

    class Config:
        case_sensitive = True

settings = Settings() 