# DockerGPT

A web application that lets you deploy Docker containers using natural language prompts. Just describe the environment you need, and the system will automatically find and deploy the right container.

## Features

- **Natural Language Input**: Enter a simple text prompt describing what you need
- **LLM + RAG**: Uses language models to understand requests and find relevant Docker images
- **Automatic Deployment**: Pulls and runs the selected Docker image with appropriate configuration
- **Container Management**: View and stop your running containers
- **Deployment Logs**: Track all deployment requests and outcomes

## Architecture

- **Frontend**: React with Material-UI
- **Backend**: Python with FastAPI
- **LLM**: OpenAI GPT models
- **Docker**: Interacts with Docker engine via Python SDK

## Getting Started

### Prerequisites

- Node.js and npm for the frontend
- Python 3.8+ for the backend
- Docker installed and running on your system
- OpenAI API key for the language model

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/RasAIGhul/docker-gpt.git
   cd docker-gpt
   ```

2. Set up the backend environment:
   ```
   cd backend
   # Create a .env file from the example or manually
   cp .env.example .env  # if .env.example exists
   # Edit .env file to add your OpenAI API key and other required variables
   ```
   
   **Important**: You must create a valid `.env` file in the `backend` directory with at least the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Set up the frontend (only needed for manual setup without Docker):
   ```
   cd ../frontend
   npm install
   ```

### Running the application

#### Option 1: Using Docker Compose (Recommended)

1. Make sure Docker is installed and running on your system

2. From the project root directory, run:
   ```
   docker-compose up --build
   ```

3. Open your browser and navigate to `http://localhost:3000`

4. To stop the application, press `Ctrl+C` in the terminal or run:
   ```
   docker-compose down
   ```

#### Option 2: Manual Setup (untested)

1. Start the backend server:
   ```
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

2. Start the frontend development server:
   ```
   cd frontend
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Example Prompts

- "Give me a Jupyter notebook with Python 3"
- "I want a Node.js environment with Express"
- "Run a basic PostgreSQL server"

## License

MIT

## Acknowledgements

- OpenAI for the GPT API
- Docker for the container platform
- Material-UI for the component library 
