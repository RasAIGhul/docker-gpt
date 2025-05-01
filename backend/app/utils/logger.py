from loguru import logger
import sys
import json
from app.core.config import settings

# Configure loguru logger
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="INFO")  # Add stderr handler with INFO level
logger.add(settings.LOG_FILE, rotation="10 MB", level="INFO")  # Add file handler

def log_prompt(prompt: str, image: str, command: str, status: str):
    """
    Log prompt and deployment details to file
    """
    log_data = {
        "prompt": prompt,
        "selected_image": image,
        "deployment_command": command,
        "status": status
    }
    
    logger.info(f"Deployment Log: {json.dumps(log_data)}")
    
    # Also append to a structured log file for demo purposes
    with open("deployment_history.json", "a") as f:
        f.write(json.dumps(log_data) + "\n") 