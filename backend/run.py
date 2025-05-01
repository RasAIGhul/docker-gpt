import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Check if environment variables are set
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("WARNING: OPENAI_API_KEY environment variable is not set.")
        print("Set it in a .env file or export it in your environment.")
    
    # Run the FastAPI application
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    ) 