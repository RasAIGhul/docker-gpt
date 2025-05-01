from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class PromptRequest(BaseModel):
    prompt: str

class ContainerConfig(BaseModel):
    name: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    ports: Optional[Dict[str, int]] = None

class ErrorDetails(BaseModel):
    type: str
    details: Optional[Dict[str, Any]] = None
    stack: Optional[str] = None

class DockerImageInfo(BaseModel):
    id: str
    repository: str
    tag: str
    size: str
    created: Optional[str] = None

class ImageDetails(BaseModel):
    name: str
    description: Optional[str] = None
    stars: Optional[int] = 0
    official: Optional[bool] = False

class DeploymentResponse(BaseModel):
    container_id: str
    image: str
    description: str
    stars: int
    status: Optional[bool] = True
    message: Optional[str] = None
    docker_command: Optional[str] = None
    process_logs: Optional[Dict[str, Any]] = None
    docker_logs: Optional[Dict[str, Any]] = None
    selected_image: Optional[ImageDetails] = None
    config: Optional[ContainerConfig] = None
    reasoning: Optional[str] = None
    error: Optional[Dict[str, Any]] = None
    access_links: Optional[Dict[str, str]] = None
    has_web_frontend: Optional[bool] = False
    web_url: Optional[str] = None

class ContainerListItem(BaseModel):
    id: str
    name: str
    image: str
    status: str
    ports: Optional[Dict[str, Any]] = {}

class ContainerListResponse(BaseModel):
    containers: List[ContainerListItem]

class ContainerActionRequest(BaseModel):
    container_id: str

class ContainerActionResponse(BaseModel):
    status: bool
    message: str
    error_details: Optional[Dict[str, Any]] = None

class ContainerConfigUpdateRequest(BaseModel):
    config_path: str
    updates: Dict[str, Any]
    restart: bool = True 