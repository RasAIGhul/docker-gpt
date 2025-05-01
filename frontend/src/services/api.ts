import axios from 'axios';
import { 
  DeploymentResponse, 
  ContainerListResponse,
  ContainerActionResponse
} from '../types/api';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const deployContainer = async (prompt: string): Promise<DeploymentResponse> => {
  try {
    console.log('DEBUG: Sending deployment request with prompt:', prompt);
    console.log('DEBUG: API URL:', API_URL);
    console.log('DEBUG: Request headers:', apiClient.defaults.headers);
    
    // Add timeout for better error diagnostics
    const response = await apiClient.post<DeploymentResponse>('/deploy', { prompt }, {
      timeout: 30000, // 30 second timeout
    });
    
    console.log('DEBUG: Deployment response received:', response.data);
    console.log('DEBUG: Response status:', response.status);
    console.log('DEBUG: Response headers:', response.headers);
    
    return response.data;
  } catch (error: any) {
    console.error('DEBUG: Error deploying container:', error);
    
    // Log detailed request information
    const requestConfig = error.config ? {
      url: error.config.url,
      method: error.config.method,
      headers: error.config.headers,
      baseURL: error.config.baseURL,
      data: error.config.data,
      timeout: error.config.timeout
    } : 'No request config available';
    
    console.error('DEBUG: Request details:', requestConfig);
    
    // Log detailed error information
    console.error('DEBUG: Error details:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      responseData: error.response?.data,
      requestMade: error.request ? true : false,
      isNetworkError: error.message?.includes('Network Error'),
      isTimeoutError: error.code === 'ECONNABORTED',
    });
    
    // Log the full error object for inspection
    console.error('DEBUG: Full error object:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
    
    // Create a standardized error response that matches DeploymentResponse structure
    const errorResponse: DeploymentResponse = {
      container_id: "",
      image: "",
      description: "",
      stars: 0,
      status: false,
      message: "",
      error: {
        type: "error",
        details: error.response?.data || error,
        stack: error.stack
      }
    };
    
    // Special handling for common errors
    if (error.message?.includes('Network Error')) {
      errorResponse.message = 'Network error connecting to backend service. Please check if the backend is running.';
      return errorResponse;
    }
    
    if (error.code === 'ECONNABORTED') {
      errorResponse.message = 'Connection timed out. The backend service might be overloaded or unresponsive.';
      return errorResponse;
    }
    
    errorResponse.message = error.response?.data?.message || 'Failed to deploy container. Please try again.';
    return errorResponse;
  }
};

export const listContainers = async (): Promise<ContainerListResponse> => {
  try {
    const response = await apiClient.get<ContainerListResponse>('/containers');
    return response.data;
  } catch (error: any) {
    console.error('Error listing containers:', error);
    return {
      containers: [],
    };
  }
};

export const stopContainer = async (containerId: string): Promise<ContainerActionResponse> => {
  try {
    const response = await apiClient.post<ContainerActionResponse>('/containers/stop', {
      container_id: containerId,
    });
    return response.data;
  } catch (error: any) {
    console.error('Error stopping container:', error);
    return {
      status: false,
      message: error.response?.data?.message || 'Failed to stop container. Please try again.',
    };
  }
};

// New functions for container and image management
export const removeContainer = async (containerId: string): Promise<ContainerActionResponse> => {
  try {
    const response = await apiClient.post<ContainerActionResponse>('/containers/remove', {
      container_id: containerId,
    });
    return response.data;
  } catch (error: any) {
    console.error('Error removing container:', error);
    return {
      status: false,
      message: error.response?.data?.message || 'Failed to remove container. Please try again.',
    };
  }
};

export interface DockerImageListResponse {
  images: Array<{
    id: string;
    repository: string;
    tag: string;
    size: string;
    created: string;
  }>;
}

export const listImages = async (): Promise<DockerImageListResponse> => {
  try {
    const response = await apiClient.get<DockerImageListResponse>('/images');
    return response.data;
  } catch (error: any) {
    console.error('Error listing images:', error);
    return {
      images: [],
    };
  }
};

export const removeImage = async (imageId: string): Promise<ContainerActionResponse> => {
  try {
    const response = await apiClient.post<ContainerActionResponse>('/images/remove', {
      container_id: imageId,
    });
    return response.data;
  } catch (error: any) {
    console.error('Error removing image:', error);
    return {
      status: false,
      message: error.response?.data?.message || 'Failed to remove image. Please try again.',
    };
  }
}; 