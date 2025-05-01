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
   git clone https://github.com/yourusername/docker-gpt.git
   cd docker-gpt
   ```

2. Set up the backend:
   ```
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env file to add your OpenAI API key
   ```

3. Set up the frontend:
   ```
   cd ../frontend
   npm install
   ```

### Running the application

1. Start the backend server:
   ```
   cd backend
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