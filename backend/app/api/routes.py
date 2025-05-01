from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict
import json
from datetime import datetime

from app.api.models import (
    PromptRequest, 
    DeploymentResponse, 
    ContainerListResponse,
    ContainerActionRequest,
    ContainerActionResponse,
    DockerImageInfo,
    ContainerConfig,
    ContainerConfigUpdateRequest
)
from app.services.docker_service import DockerService
from app.services.llm_service import LLMService
from app.utils.logger import log_prompt, logger

router = APIRouter()

# Dependencies
def get_docker_service():
    return DockerService()

def get_llm_service():
    return LLMService()

@router.post("/deploy", response_model=DeploymentResponse)
async def deploy_container(deployment_request: PromptRequest,
                          llm_service: LLMService = Depends(get_llm_service),
                          docker_service: DockerService = Depends(get_docker_service)):
    """
    Deploy a Docker container based on the provided prompt
    """
    try:
        logger.info(f"Received deployment request with prompt: {deployment_request.prompt}")
        deployment_logs = []
        deployment_logs.append(f"Received deployment request with prompt: {deployment_request.prompt}")
        
        # Process the prompt using LLM
        llm_error = None
        llm_logs = []
        try:
            deployment_logs.append("Processing prompt with language model...")
            llm_response = await llm_service.process_prompt(deployment_request.prompt)
            logger.info(f"LLM response: {llm_response}")
            deployment_logs.append(f"Language model selected image: {llm_response['image']}")
            is_fallback = False
        except Exception as e:
            llm_error = str(e)
            deployment_logs.append(f"Error during LLM processing: {llm_error}")
            logger.error(f"Error during LLM processing: {llm_error}")
            logger.exception("LLM processing exception details:")
            # Fallback to default image if LLM processing fails
            llm_response = {
                "image": "nginx",
                "description": "Fallback to Nginx web server due to LLM processing error",
                "stars": 10000
            }
            deployment_logs.append(f"Using fallback image: {llm_response['image']}")
            is_fallback = True
        
        # Run the Docker container
        try:
            deployment_logs.append(f"Starting Docker container with image: {llm_response['image']}")
            logger.info(f"Running container with image: {llm_response['image']}")
            
            # Generate container configuration (ports, env vars)
            config = llm_service._generate_container_config(deployment_request.prompt, llm_response)
            deployment_logs.append(f"Generated container configuration: ports={config.get('ports', {})} environment={list(config.get('environment', {}).keys())}")
            
            # Run the container with the configuration
            container_id, command, process_logs = docker_service.run_container(
                llm_response["image"],
                ports=config.get("ports"),
                env=config.get("environment")
            )
            
            logger.info(f"Container deployed successfully with ID: {container_id}")
            logger.info(f"Command executed: {command}")
            deployment_logs.append(f"Container deployed successfully with ID: {container_id}")
        except Exception as e:
            deployment_logs.append(f"Error during container deployment: {str(e)}")
            logger.error(f"Error during container deployment: {str(e)}")
            logger.exception("Container deployment exception details:")
            
            # Create a detailed error response with logs
            error_detail = {
                "message": f"Failed to deploy container: {str(e)}",
                "logs": deployment_logs,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            # Try to extract error details if available
            error_details = {}
            if isinstance(e, Exception) and hasattr(e, 'args') and len(e.args) > 0:
                if isinstance(e.args[0], str) and "Error running container" in e.args[0]:
                    error_details["cause"] = "Docker container execution failed"
                if "Failed to pull image" in str(e):
                    error_details["cause"] = "Failed to pull Docker image"
                    
            error_detail["details"] = error_details
            
            # Return error with all available details
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to deploy container: {str(e)}"
            )
        
        # Return the deployment response
        response = DeploymentResponse(
            container_id=container_id,
            image=llm_response["image"],
            description=llm_response["description"],
            stars=llm_response["stars"],
            status=True,
            message=f"Container deployed successfully{' (using fallback image)' if is_fallback else ''}",
            docker_command=command,
            process_logs=process_logs,
            docker_logs=process_logs,
            selected_image={
                "name": llm_response["image"],
                "description": llm_response["description"],
                "stars": llm_response["stars"],
                "official": False
            },
            access_links=process_logs.get("access_links"),
            has_web_frontend=process_logs.get("has_web_frontend", False),
            web_url=process_logs.get("web_url")
        )
        
        # Add error information if fallback was used
        if is_fallback and llm_error:
            response.error = {
                "type": "LLM_PROCESSING_ERROR",
                "details": {
                    "error": llm_error,
                    "fallback_used": True,
                    "original_prompt": deployment_request.prompt,
                    "fallback_image": llm_response["image"],
                    "logs": deployment_logs
                }
            }
            
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in deploy endpoint: {str(e)}")
        logger.exception("Deployment endpoint exception details:")
        # Log the type of exception and its attributes for better debugging
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception attributes: {dir(e)}")
        if hasattr(e, 'args'):
            logger.error(f"Exception args: {e.args}")
        if hasattr(e, '__traceback__'):
            import traceback
            logger.error(f"Exception traceback: {traceback.format_exc()}")
        
        raise HTTPException(status_code=500, detail=f"Failed to process deployment: {str(e)}")

@router.get("/containers", response_model=ContainerListResponse)
def list_containers(docker_service: DockerService = Depends(get_docker_service)):
    """
    List all running Docker containers
    """
    containers = docker_service.list_running_containers()
    return ContainerListResponse(containers=containers)

@router.post("/containers/stop", response_model=ContainerActionResponse)
def stop_container(
    request: ContainerActionRequest,
    docker_service: DockerService = Depends(get_docker_service)
):
    """
    Stop a running Docker container
    """
    success, message, error_details = docker_service.stop_container(request.container_id)
    return ContainerActionResponse(status=success, message=message, error_details=error_details)

@router.post("/containers/remove", response_model=ContainerActionResponse)
def remove_container(
    request: ContainerActionRequest,
    docker_service: DockerService = Depends(get_docker_service)
):
    """
    Remove a Docker container
    """
    success, message, error_details = docker_service.remove_container(request.container_id)
    return ContainerActionResponse(status=success, message=message, error_details=error_details)

@router.get("/images", response_model=dict)
def list_images(docker_service: DockerService = Depends(get_docker_service)):
    """
    List all Docker images
    """
    images = docker_service.list_images()
    return {"images": images}

@router.post("/images/remove", response_model=ContainerActionResponse)
def remove_image(
    request: ContainerActionRequest,
    docker_service: DockerService = Depends(get_docker_service)
):
    """
    Remove a Docker image
    """
    success, message, error_details = docker_service.remove_image(request.container_id)
    return ContainerActionResponse(status=success, message=message, error_details=error_details)

@router.get("/images/search")
async def search_images(
    query: str,
    docker_service: DockerService = Depends(get_docker_service)
):
    """
    Search for Docker images on Docker Hub
    """
    images = await docker_service.search_images(query)
    return {"images": images}

@router.post("/containers/{container_id}/config", response_model=ContainerActionResponse)
def update_container_config(
    container_id: str,
    request: ContainerConfigUpdateRequest,
    docker_service: DockerService = Depends(get_docker_service)
):
    """
    Update configuration for a running container
    """
    success, message, logs = docker_service.update_container_config(
        container_id, 
        request.config_path, 
        request.updates
    )
    
    return ContainerActionResponse(
        status=success, 
        message=message, 
        error_details=None if success else logs.get("error_details", {}),
        logs=logs
    ) 