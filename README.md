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

#### Option 1: Using Docker Compose (Recommended for Development)

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

#### Option 3: Using Docker Hub Images (Recommended for Deployment)

The application is available as pre-built Docker images on Docker Hub, which means you don't need to build them yourself:

1. Clone this repository (for the configuration files only):
   ```
   git clone https://github.com/RasAIGhul/docker-gpt.git
   cd docker-gpt
   ```

2. Create a `.env` file in the `backend` directory with your OpenAI API key:
   ```
   cd backend
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   cd ..
   ```

3. Create a simple `docker-compose.yml` file or use the one in the repository:
   ```yaml
   version: '3.8'
   
   services:
     backend:
       image: zcondeelis/docker-gpt-backend:latest
       ports:
         - "8000:8000"
       volumes:
         - /var/run/docker.sock:/var/run/docker.sock
         - $HOME/.docker/run:$HOME/.docker/run
         - ./backend/.env:/app/.env
       environment:
         - DOCKER_HOST=unix:///var/run/docker.sock
       restart: always
   
     frontend:
       image: zcondeelis/docker-gpt-frontend:latest
       ports:
         - "3000:3000"
       environment:
         - REACT_APP_API_URL=http://localhost:8000/api/v1
       depends_on:
         - backend
       restart: always
   ```

4. Start the application with a single command (no building needed):
   ```
   docker-compose up
   ```

5. Open your browser and navigate to `http://localhost:3000`

6. To stop the application, press `Ctrl+C` in the terminal or run:
   ```
   docker-compose down
   ```

**Note**: This approach uses the same microservice architecture as the local build but leverages pre-built images from Docker Hub for convenience.

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
