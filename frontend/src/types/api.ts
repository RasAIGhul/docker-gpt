export interface PromptRequest {
  prompt: string;
}

export interface DockerImageInfo {
  name: string;
  description?: string;
  stars?: number;
  official?: boolean;
}

export interface ContainerConfig {
  name?: string;
  environment?: Record<string, string>;
  ports?: Record<string, number>;
}

export interface DeploymentResponse {
  container_id: string;
  image: string;
  description: string;
  stars: number;
  status: boolean;
  message: string;
  docker_command?: string;
  process_logs?: {
    steps: string[];
    image: string;
    timestamp: string;
    success: boolean;
    error?: string;
    container_id?: string;
  };
  docker_logs?: any;
  selected_image?: DockerImageInfo;
  config?: ContainerConfig;
  reasoning?: string;
  error?: {
    type: string;
    details: any;
    stack?: string;
  };
  access_links?: Record<string, string>;
  has_web_frontend?: boolean;
  web_url?: string;
}

export interface ContainerListItem {
  id: string;
  name: string;
  image: string;
  status: string;
  ports?: Record<string, any>;
}

export interface ContainerListResponse {
  containers: ContainerListItem[];
}

export interface ContainerActionRequest {
  container_id: string;
}

export interface ContainerActionResponse {
  status: boolean;
  message: string;
  error_details?: any;
}

export interface DockerImageListItem {
  id: string;
  repository: string;
  tag: string;
  size: string;
  created?: string;
}

export interface DockerImageListResponse {
  images: DockerImageListItem[];
} 