import subprocess
import json
import httpx
import os
from typing import Dict, List, Optional, Tuple
from app.utils.logger import logger
import traceback
from datetime import datetime
import socket
import random

class DockerService:
    def __init__(self):
        try:
            # Verify that docker CLI is available
            result = self._run_docker_command(["version", "--format", "{{json .}}"])
            if result[0]:
                logger.info("Successfully connected to Docker using CLI")
            else:
                raise Exception(f"Docker CLI test failed: {result[1]}")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {str(e)}")
            raise
            
        # Correct Docker Hub API URL - use the publicly accessible API
        self.hub_api_url = "https://hub.docker.com/api"
    
    def _is_port_available(self, port: int) -> bool:
        """
        Check if a port is available for use
        
        Args:
            port: The port number to check
            
        Returns:
            Boolean indicating if the port is available
        """
        try:
            # Create a socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Try to bind to the port - if it succeeds, the port is available
                s.bind(('', port))
                return True
        except:
            # If binding fails, the port is in use
            return False
            
    def _find_available_port(self, start_port: int, end_port: int = 9000) -> int:
        """
        Find an available port within a range
        
        Args:
            start_port: The starting port number to check
            end_port: The ending port number (default: 9000)
            
        Returns:
            An available port number, or -1 if none found
        """
        # Try the specific port first
        if self._is_port_available(start_port):
            return start_port
            
        # If not available, try a random port in the range
        for _ in range(10):  # Try 10 random ports
            port = random.randint(start_port + 1, end_port)
            if self._is_port_available(port):
                return port
                
        # If still not found, sequentially check ports in the range
        for port in range(start_port + 1, end_port + 1):
            if self._is_port_available(port):
                return port
                
        # No available ports found
        return -1
    
    def _run_docker_command(self, args: List[str]) -> Tuple[bool, str, Optional[dict]]:
        """Run a docker command and return the result"""
        cmd = ["docker"] + args
        try:
            logger.info(f"Running docker command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                # Try to parse as JSON if possible
                try:
                    if result.stdout.strip():
                        return True, result.stdout, json.loads(result.stdout)
                    return True, "", None
                except json.JSONDecodeError:
                    return True, result.stdout, None
            else:
                logger.error(f"Docker command failed: {result.stderr}")
                return False, result.stderr, None
        except Exception as e:
            logger.error(f"Error running docker command: {str(e)}")
            return False, str(e), None
    
    async def search_images(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search Docker Hub for images based on query
        """
        try:
            logger.info(f"Searching Docker Hub for query: {query}")
            
            # Direct fallback to CLI search as the API is not working
            logger.info("Using fallback Docker CLI search directly instead of API")
            return self._fallback_search(query, limit)
            
        except Exception as e:
            logger.error(f"Error searching Docker Hub: {str(e)}")
            # Fall back to default images if all else fails
            return self._default_images(query)
    
    def _fallback_search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Fallback to using docker search CLI command when API fails
        """
        logger.info(f"Using fallback docker search for query: {query}")
        
        # Use docker search command as fallback
        success, output, parsed = self._run_docker_command([
            "search", 
            "--format", "{{json .}}", 
            "--limit", str(limit), 
            query
        ])
        
        if not success or not output:
            logger.error("Docker search command failed")
            # Last resort: return some default images related to the query
            return self._default_images(query)
        
        try:
            # Parse the output as JSON (each line is a separate JSON object)
            images = []
            for line in output.strip().split("\n"):
                if not line:
                    continue
                    
                try:
                    image_data = json.loads(line)
                    # Convert to our format
                    images.append({
                        "name": image_data.get("Name", ""),
                        "description": image_data.get("Description", ""),
                        "stars": image_data.get("StarCount", 0),
                        "official": image_data.get("IsOfficial", "") == "[OK]"
                    })
                except json.JSONDecodeError:
                    continue
            
            logger.info(f"Found {len(images)} images from docker search command")
            return images
        except Exception as e:
            logger.error(f"Error parsing docker search results: {str(e)}")
            return self._default_images(query)
    
    def _default_images(self, query: str) -> List[Dict]:
        """
        Return some default images based on common keywords in the query
        """
        logger.info("Using default image selection based on keywords")
        
        default_images = []
        
        # Node.js related
        if any(kw in query.lower() for kw in ["node", "javascript", "express", "js"]):
            default_images.append({
                "name": "node",
                "description": "Node.js is a JavaScript-based platform for server-side and networking applications",
                "stars": 10000,
                "official": True
            })
        
        # Python related
        if any(kw in query.lower() for kw in ["python", "flask", "django", "jupyter"]):
            default_images.append({
                "name": "python",
                "description": "Python is an interpreted, interactive, object-oriented, open-source programming language",
                "stars": 10000,
                "official": True
            })
            
            # Jupyter specific
            if "jupyter" in query.lower() or "notebook" in query.lower():
                default_images.append({
                    "name": "jupyter/minimal-notebook",
                    "description": "Jupyter Notebook Scientific Python Stack",
                    "stars": 5000,
                    "official": False
                })
        
        # Database related
        if any(kw in query.lower() for kw in ["database", "db", "sql", "postgres", "postgresql"]):
            default_images.append({
                "name": "postgres",
                "description": "The PostgreSQL object-relational database system",
                "stars": 10000,
                "official": True
            })
            
        if any(kw in query.lower() for kw in ["mysql", "mariadb"]):
            default_images.append({
                "name": "mysql",
                "description": "MySQL is a widely used, open-source relational database management system",
                "stars": 10000,
                "official": True
            })
        
        # If no specific matches, add some general purpose images
        if not default_images:
            default_images = [
                {
                    "name": "ubuntu",
                    "description": "Ubuntu is a Debian-based Linux operating system",
                    "stars": 10000,
                    "official": True
                },
                {
                    "name": "nginx",
                    "description": "Official build of Nginx",
                    "stars": 10000,
                    "official": True
                },
                {
                    "name": "alpine",
                    "description": "A minimal Docker image based on Alpine Linux",
                    "stars": 10000,
                    "official": True
                }
            ]
        
        logger.info(f"Selected {len(default_images)} default images based on query")
        return default_images

    def pull_image(self, image_name: str) -> Tuple[bool, str]:
        """
        Pull Docker image from registry
        """
        try:
            logger.info(f"Pulling image: {image_name}")
            success, output, _ = self._run_docker_command(["pull", image_name])
            if success:
                return True, f"Successfully pulled image {image_name}"
            else:
                return False, f"Error pulling image {image_name}: {output}"
        except Exception as e:
            error_msg = f"Error pulling image {image_name}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _generate_access_links(self, image_name: str, ports: Dict[str, int]) -> Dict[str, str]:
        """
        Generate access links for a container based on its ports
        Returns a dictionary of {link_type: url}
        """
        links = {}
        image_lower = image_name.lower()
        
        # No ports means no access links
        if not ports:
            return links
        
        # Categorize ports by their typical usage
        port_categories = {
            # Web UI ports
            "web": ["80", "8080", "3000", "8000", "8888", "5173", "5000"],
            
            # Database ports
            "database": {
                "5432": "postgresql://localhost:{}", # PostgreSQL
                "3306": "mysql://localhost:{}", # MySQL/MariaDB
                "27017": "mongodb://localhost:{}", # MongoDB
                "1433": "sqlserver://localhost:{}", # MSSQL
                "6379": "redis://localhost:{}", # Redis
            },
            
            # Admin interfaces
            "admin": {
                "15672": ["rabbit"], # RabbitMQ
                "8080": ["tomcat"], # Tomcat
                "9000": ["portainer", "sonatype", "nexus"], # Admin tools
            },
            
            # Special applications
            "special": {
                "8096": ["jellyfin", "emby"], # Media servers
                "32400": ["plex"], # Plex (append /web to URL)
                "8888": ["jupyter"], # Jupyter notebooks
                "3000": ["grafana"], # Grafana dashboards
                "5601": ["kibana"], # Kibana
            }
        }
        
        # Process each port mapping
        for container_port, host_port in ports.items():
            # Extract the port number without the protocol
            if '/' in container_port:
                port_number = container_port.split('/')[0]
            else:
                port_number = container_port
                
            # Special case for media servers
            if "jellyfin" in image_lower and port_number == "8096":
                links['web'] = f"http://localhost:{host_port}"
                continue
                
            if "plex" in image_lower and port_number == "32400":
                links['web'] = f"http://localhost:{host_port}/web"
                continue
                
            # Check for web UI ports
            if port_number in port_categories["web"]:
                links['web'] = f"http://localhost:{host_port}"
                
            # Check for database ports with specific connection strings
            if port_number in port_categories["database"]:
                conn_string_template = port_categories["database"][port_number]
                links['database'] = conn_string_template.format(host_port)
                
            # Check for admin interfaces
            if port_number in port_categories["admin"]:
                image_patterns = port_categories["admin"][port_number]
                if any(pattern in image_lower for pattern in image_patterns):
                    links['admin'] = f"http://localhost:{host_port}"
                    
            # Check for special applications
            if port_number in port_categories["special"]:
                image_patterns = port_categories["special"][port_number]
                if any(pattern in image_lower for pattern in image_patterns):
                    # For Jupyter notebooks
                    if "jupyter" in image_lower and port_number == "8888":
                        links['jupyter'] = f"http://localhost:{host_port}"
                    # For dashboard applications
                    elif any(name in image_lower for name in ["grafana", "kibana"]):
                        links['dashboard'] = f"http://localhost:{host_port}"
                    # General web interface for other special apps
                    else:
                        links['web'] = f"http://localhost:{host_port}"
                
        # If no web link was set but the container likely has a web UI, use the first mapped port
        if not links.get('web') and any(server in image_lower for server in 
            ['nginx', 'httpd', 'apache', 'web', 'node', 'express', 'react', 'vue', 'angular', 'php', 'wordpress']):
            # Find the first mapped port and use it
            if ports:
                container_port, host_port = next(iter(ports.items()))
                links['web'] = f"http://localhost:{host_port}"
                
        return links

    def run_container(self, image_name: str, ports: Optional[Dict[str, int]] = None, env: Optional[Dict[str, str]] = None) -> Tuple[str, str, Dict]:
        """
        Run a Docker container with the specified image and configuration
        
        Args:
            image_name: The name of the Docker image to run
            ports: Optional port mappings {container_port: host_port}
            env: Optional environment variables
            
        Returns:
            Tuple containing:
            - The ID of the created container
            - The Docker command that was executed
            - A dict with detailed logs of each step in the process
        """
        process_logs = {
            "steps": [],
            "image": image_name,
            "timestamp": datetime.now().isoformat(),
            "success": False
        }
        
        # Track port allocation attempts to avoid infinite loops
        port_attempt = 0
        max_port_attempts = 3
        original_ports = ports.copy() if ports else None
        
        # Start of retry loop for port allocation issues
        while port_attempt <= max_port_attempts:
            try:
                if port_attempt > 0:
                    log_msg = f"Port allocation retry attempt {port_attempt} of {max_port_attempts}"
                    logger.info(log_msg)
                    process_logs["steps"].append(log_msg)
                
                log_msg = f"Preparing to run container with image: {image_name}"
                logger.info(log_msg)
                process_logs["steps"].append(log_msg)
                
                # Build the docker run command
                cmd = ["run", "-d"]  # Detached mode
                
                # Verify the image exists or can be pulled
                log_msg = f"Verifying image '{image_name}' exists"
                logger.info(log_msg)
                process_logs["steps"].append(log_msg)
                
                image_exists, verify_msg, verify_details = self.verify_image_exists(image_name)
                process_logs["steps"].append(verify_msg)
                process_logs["verify_details"] = verify_details
                
                if not image_exists:
                    # Try to find alternatives
                    log_msg = f"Image '{image_name}' verification failed. Finding alternatives..."
                    logger.warning(log_msg)
                    process_logs["steps"].append(log_msg)
                    
                    alternatives = self.suggest_alternative_images(image_name)
                    
                    if alternatives:
                        alternative_msg = f"Found alternative images: {', '.join([alt['name'] for alt in alternatives])}"
                        logger.info(alternative_msg)
                        process_logs["steps"].append(alternative_msg)
                        process_logs["alternatives"] = alternatives
                        
                        # Use the first alternative
                        alt_image = alternatives[0]["name"]
                        alt_reason = alternatives[0]["reason"]
                        log_msg = f"Using alternative image '{alt_image}': {alt_reason}"
                        logger.info(log_msg)
                        process_logs["steps"].append(log_msg)
                        
                        # Update the image name to the alternative
                        image_name = alt_image
                        process_logs["image"] = alt_image
                        process_logs["alternative_used"] = True
                        process_logs["alternative_reason"] = alt_reason
                    else:
                        # No alternatives found, give up
                        error_msg = f"No valid alternative images found for '{image_name}'"
                        logger.error(error_msg)
                        process_logs["steps"].append(error_msg)
                        process_logs["error"] = "IMAGE_NOT_FOUND_NO_ALTERNATIVES"
                        process_logs["error_details"] = {
                            "image": image_name,
                            "verification": verify_details,
                            "message": error_msg
                        }
                        raise Exception(f"Failed to find valid image: {error_msg}")
                
                # Check if image exists locally
                check_image_cmd = ["images", image_name, "--quiet"]
                image_exists, image_output, _ = self._run_docker_command(check_image_cmd)
                
                if not image_output:
                    log_msg = f"Image '{image_name}' not found locally, attempting to pull..."
                    logger.info(log_msg)
                    process_logs["steps"].append(log_msg)
                    
                    # Try to pull the image
                    pull_cmd = ["pull", image_name]
                    pull_success, pull_output, pull_stderr = self._run_docker_command(pull_cmd)
                    
                    if not pull_success:
                        log_msg = f"Failed to pull image '{image_name}': {pull_stderr}"
                        logger.error(log_msg)
                        process_logs["steps"].append(log_msg)
                        process_logs["error"] = pull_stderr
                        process_logs["error_details"] = {
                            "command": f"docker pull {image_name}",
                            "stderr": pull_stderr,
                            "stdout": pull_output,
                            "type": "PULL_ERROR"
                        }
                        raise Exception(f"Failed to pull image '{image_name}': {pull_stderr}")
                    
                    log_msg = f"Successfully pulled image '{image_name}'"
                    logger.info(log_msg)
                    process_logs["steps"].append(log_msg)
                else:
                    log_msg = f"Image '{image_name}' found locally"
                    logger.info(log_msg)
                    process_logs["steps"].append(log_msg)
                
                # Auto-detect ports if none provided based on common image types
                if not ports:
                    # Try to find exposed ports in the image
                    try:
                        logger.info(f"Attempting to detect ports from image: {image_name}")
                        success, output, parsed = self._run_docker_command(["image", "inspect", image_name])
                        
                        if success and parsed and isinstance(parsed, list) and len(parsed) > 0:
                            # Extract exposed ports from image config
                            config = parsed[0].get("Config", {})
                            exposed_ports = config.get("ExposedPorts", {})
                            
                            if exposed_ports:
                                # Get dynamically mapped ports based on the exposed ports
                                auto_ports = {}
                                image_lower = image_name.lower()
                                
                                # Check for special cases like Jellyfin with multiple important ports
                                if "jellyfin" in image_lower and "80/tcp" in exposed_ports and "8096/tcp" in exposed_ports:
                                    logger.info(f"Detected Jellyfin image with both ports 80 (web) and 8096 (API) exposed")
                                    process_logs["steps"].append(f"Detected Jellyfin with multiple important ports (80/tcp, 8096/tcp)")
                                    
                                    # Find available ports for both
                                    port_80 = self._find_available_port(8080)
                                    port_8096 = self._find_available_port(8096)
                                    
                                    if port_80 > 0 and port_8096 > 0:
                                        auto_ports["80/tcp"] = port_80
                                        auto_ports["8096/tcp"] = port_8096
                                        
                                        logger.info(f"Mapping Jellyfin ports: 80/tcp → {port_80}, 8096/tcp → {port_8096}")
                                        process_logs["steps"].append(f"Dynamically mapped multiple Jellyfin ports: 80/tcp → {port_80}, 8096/tcp → {port_8096}")
                                        process_logs["multi_port_mapping"] = True
                                # Process each exposed port for other cases
                                else:
                                    # Categorize ports for priority mapping
                                    priority_mappings = {
                                        "web": ["80/tcp", "8080/tcp", "3000/tcp", "8000/tcp"],
                                        "api": ["8096/tcp", "8888/tcp", "5000/tcp"],
                                        "database": ["5432/tcp", "3306/tcp", "27017/tcp", "6379/tcp"],
                                        "other": []
                                    }
                                    
                                    # Flat list of all priority ports
                                    all_priority_ports = []
                                    for category, port_list in priority_mappings.items():
                                        all_priority_ports.extend(port_list)
                                        
                                    # Organize ports by priority
                                    high_priority_ports = []
                                    normal_priority_ports = []
                                    
                                    for port in exposed_ports.keys():
                                        if port in all_priority_ports:
                                            high_priority_ports.append(port)
                                        else:
                                            normal_priority_ports.append(port)
                                    
                                    # Process ports in priority order
                                    for port in high_priority_ports + normal_priority_ports:
                                        try:
                                            port_number = int(port.split("/")[0])
                                            
                                            # Try to use the same port number if available and > 1024
                                            preferred_port = port_number
                                            if port_number < 1024:
                                                # For well-known ports, use conventional mappings
                                                if port_number == 80:
                                                    preferred_port = 8080
                                                elif port_number == 443:
                                                    preferred_port = 8443
                                                else:
                                                    preferred_port = 8000 + port_number
                                            
                                            # Check if preferred port is available
                                            if self._is_port_available(preferred_port):
                                                auto_ports[port] = preferred_port
                                            else:
                                                # Find an alternative port
                                                alt_port = self._find_available_port(preferred_port)
                                                if alt_port > 0:
                                                    auto_ports[port] = alt_port
                                        except ValueError:
                                            continue
                                
                                if auto_ports:
                                    log_msg = f"Dynamically discovered and mapped ports: {auto_ports}"
                                    logger.info(log_msg)
                                    process_logs["steps"].append(log_msg)
                                    ports = auto_ports
                                    process_logs["auto_port_mapping"] = True
                                    process_logs["detected_from_image"] = True
                    except Exception as e:
                        log_msg = f"Error detecting ports from image: {str(e)}"
                        logger.warning(log_msg)
                        process_logs["steps"].append(log_msg)
                    
                    # If no ports found from image inspection, use default mappings
                    if not ports:
                        auto_ports = self._get_default_port_mappings(image_name)
                        if auto_ports:
                            log_msg = f"No ports detected from image, using default mappings for {image_name}: {auto_ports}"
                            logger.info(log_msg)
                            process_logs["steps"].append(log_msg)
                            ports = auto_ports
                            process_logs["auto_port_mapping"] = True
                
                # If this is a retry attempt with port conflict, adjust ports
                if port_attempt > 0 and ports:
                    adjusted_ports = {}
                    for container_port, host_port in ports.items():
                        # Try to find a new available port
                        new_port = self._find_available_port(host_port + 1000)
                        if new_port > 0:
                            adjusted_ports[container_port] = new_port
                            log_msg = f"Retry attempt {port_attempt}: Using port {new_port} instead of {host_port}"
                            logger.info(log_msg)
                            process_logs["steps"].append(log_msg)
                        else:
                            # If we can't find a new port, just increment by 1000 * attempt number
                            # This is a fallback and might still fail
                            fallback_port = host_port + (port_attempt * 1000)
                            adjusted_ports[container_port] = fallback_port
                            log_msg = f"Retry attempt {port_attempt}: Using fallback port {fallback_port} instead of {host_port}"
                            logger.info(log_msg)
                            process_logs["steps"].append(log_msg)
                    
                    # Store the original ports for reference
                    if port_attempt == 1:
                        process_logs["original_ports"] = original_ports
                        
                    process_logs[f"adjusted_ports_attempt_{port_attempt}"] = adjusted_ports
                    ports = adjusted_ports
                
                # Add port mappings if provided
                if ports:
                    log_msg = f"Adding port mappings: {ports}"
                    process_logs["steps"].append(log_msg)
                    
                    for container_port, host_port in ports.items():
                        cmd.extend(["-p", f"{host_port}:{container_port}"])
                else:
                    warning_msg = "WARNING: No port mappings provided or detected. Container may not be accessible."
                    logger.warning(warning_msg)
                    process_logs["steps"].append(warning_msg)
                
                # Add environment variables if provided
                if env:
                    log_msg = f"Adding environment variables: {list(env.keys())}"
                    process_logs["steps"].append(log_msg)
                    for key, value in env.items():
                        cmd.extend(["-e", f"{key}={value}"])
                    
                # Add the image name
                cmd.append(image_name)
                
                # Capture the full command for logging/debugging
                full_command = "docker " + " ".join(cmd)
                log_msg = f"Executing command: {full_command}"
                logger.info(log_msg)
                process_logs["steps"].append(log_msg)
                
                # Execute the command
                success, output, stderr = self._run_docker_command(cmd)
                
                if not success:
                    error_msg = f"Failed to run container: {stderr or output}"
                    logger.error(error_msg)
                    process_logs["steps"].append(error_msg)
                    
                    # Check if error is related to port allocation
                    if stderr and "Bind for 0.0.0.0:" in stderr and "port is already allocated" in stderr and port_attempt < max_port_attempts:
                        log_msg = f"Port allocation error detected, will try with different ports on next attempt"
                        logger.warning(log_msg)
                        process_logs["steps"].append(log_msg)
                        port_attempt += 1
                        continue
                    else:
                        process_logs["error"] = stderr or output
                        process_logs["error_details"] = {
                            "command": full_command,
                            "stderr": stderr,
                            "stdout": output,
                            "type": "RUN_ERROR"
                        }
                        raise Exception(error_msg)
                
                # The output should be the container ID
                container_id = output.strip()
                log_msg = f"Container started successfully with ID: {container_id}"
                logger.info(log_msg)
                process_logs["steps"].append(log_msg)
                process_logs["container_id"] = container_id
                process_logs["success"] = True
                
                # Generate access links if ports were mapped
                if ports:
                    access_links = self._generate_access_links(image_name, ports)
                    if access_links:
                        link_msg = f"Container can be accessed at: {', '.join([f'{k}: {v}' for k, v in access_links.items()])}"
                        logger.info(link_msg)
                        process_logs["steps"].append(link_msg)
                        process_logs["access_links"] = access_links
                        
                        # Add a specific flag if it has a web frontend
                        if 'web' in access_links:
                            process_logs["has_web_frontend"] = True
                            process_logs["web_url"] = access_links['web']
                
                return container_id, full_command, process_logs
                
            except Exception as e:
                # If this is a port allocation error and we haven't exceeded retry attempts
                error_str = str(e)
                if error_str and "port is already allocated" in error_str and port_attempt < max_port_attempts:
                    log_msg = f"Port allocation error: {error_str}"
                    logger.warning(log_msg)
                    process_logs["steps"].append(log_msg)
                    port_attempt += 1
                    # Continue with the next attempt
                    continue
                else:
                    # For non-port errors or if we've exceeded retry attempts
                    error_msg = f"Error running container: {error_str}"
                    logger.error(error_msg)
                    logger.exception("Container run exception details:")
                    process_logs["steps"].append(error_msg)
                    process_logs["error"] = error_str
                    
                    # Add more detailed error information
                    error_details = {
                        "exception": error_str,
                        "exception_type": type(e).__name__,
                        "traceback": traceback.format_exc(),
                        "type": "EXCEPTION"
                    }
                    
                    # Log additional details about the error
                    logger.error(f"Exception type: {type(e).__name__}")
                    if hasattr(e, 'args'):
                        logger.error(f"Exception args: {e.args}")
                        error_details["args"] = str(e.args)
                    
                    process_logs["error_details"] = error_details
                    
                    # Return process logs with the error instead of raising exception
                    return "", f"docker run failed: {error_str}", process_logs

    def _get_default_port_mappings(self, image_name: str) -> Dict[str, int]:
        """
        Get default port mappings for common container types
        Returns a dict of {container_port: host_port}
        """
        # First try to inspect the image to find exposed ports
        try:
            logger.info(f"Dynamically discovering exposed ports for image {image_name}")
            success, output, parsed = self._run_docker_command(["image", "inspect", image_name])
            
            if success and parsed and isinstance(parsed, list) and len(parsed) > 0:
                # Extract exposed ports from image config
                config = parsed[0].get("Config", {})
                exposed_ports = config.get("ExposedPorts", {})
                
                if exposed_ports:
                    # Convert exposed ports to our format with intelligent mapping
                    mapped_ports = {}
                    image_lower = image_name.lower()
                    
                    # For special known port handling - this gives us default port preferences
                    # but doesn't restrict us to only these ports
                    port_preferences = {
                        "web": ["80/tcp", "8080/tcp", "3000/tcp", "8000/tcp", "5000/tcp", "8888/tcp"],
                        "database": ["5432/tcp", "3306/tcp", "27017/tcp", "6379/tcp", "1433/tcp"],
                        "api": ["8096/tcp", "9000/tcp", "8081/tcp"],
                        "admin": ["8080/tcp", "9090/tcp", "15672/tcp"]
                    }
                    
                    # Create a mapping of port numbers to categories for easier reference
                    port_to_category = {}
                    for category, port_list in port_preferences.items():
                        for port in port_list:
                            port_to_category[port] = category
                    
                    # Prioritize essential ports based on image type
                    primary_ports = []
                    secondary_ports = []
                    
                    # Categorize detected ports
                    for port in exposed_ports.keys():
                        if "jellyfin" in image_lower and port in ["8096/tcp", "80/tcp"]:
                            # Special case for Jellyfin with both ports exposed
                            primary_ports.append(port)
                        elif "plex" in image_lower and port == "32400/tcp":
                            # Special case for Plex
                            primary_ports.append(port)
                        elif port in port_to_category:
                            if port_to_category[port] == "web" or port_to_category[port] == "api":
                                primary_ports.append(port)
                            else:
                                secondary_ports.append(port)
                        else:
                            secondary_ports.append(port)
                    
                    # Map primary ports first, then secondary
                    for port in primary_ports + secondary_ports:
                        try:
                            port_number = int(port.split("/")[0])
                            
                            # Try to use the same port number if available
                            if self._is_port_available(port_number):
                                mapped_ports[port] = port_number
                            else:
                                # Find an alternative port
                                base_port = 8000 if port_number < 1024 else port_number
                                alt_port = self._find_available_port(base_port)
                                if alt_port > 0:
                                    mapped_ports[port] = alt_port
                        except ValueError:
                            continue
                    
                    if mapped_ports:
                        logger.info(f"Dynamically mapped ports for {image_name}: {mapped_ports}")
                        return mapped_ports
        except Exception as e:
            logger.warning(f"Error inspecting image for exposed ports: {str(e)}")
        
        # If no ports found from dynamic inspection, fall back to default mappings for known images
        image_lower = image_name.lower()
        base_name = image_lower.split('/')[-1].split(':')[0]
        
        # Default port mappings for common images - these are fallbacks when inspection fails
        default_ports = {
            # Web servers
            "nginx": {"80/tcp": 8080},
            "httpd": {"80/tcp": 8080},
            "apache": {"80/tcp": 8080},
            "traefik": {"80/tcp": 8080, "8080/tcp": 8081},
            
            # Application servers
            "tomcat": {"8080/tcp": 8080},
            "jetty": {"8080/tcp": 8080},
            
            # Databases
            "mysql": {"3306/tcp": 3306},
            "mariadb": {"3306/tcp": 3306},
            "postgres": {"5432/tcp": 5432},
            "postgresql": {"5432/tcp": 5432},
            "mongo": {"27017/tcp": 27017},
            "mongodb": {"27017/tcp": 27017},
            "redis": {"6379/tcp": 6379},
            "mssql": {"1433/tcp": 1433},
            
            # Message brokers
            "rabbitmq": {"5672/tcp": 5672, "15672/tcp": 15672},
            "kafka": {"9092/tcp": 9092},
            
            # Elastic stack
            "elasticsearch": {"9200/tcp": 9200, "9300/tcp": 9300},
            "kibana": {"5601/tcp": 5601},
            "logstash": {"5044/tcp": 5044, "9600/tcp": 9600},
            
            # Other common services
            "grafana": {"3000/tcp": 3000},
            "prometheus": {"9090/tcp": 9090},
            "jenkins": {"8080/tcp": 8080, "50000/tcp": 50000},
            
            # Media servers and applications
            "jellyfin": {"8096/tcp": 8096, "80/tcp": 8080},
            "plex": {"32400/tcp": 32400},
            "emby": {"8096/tcp": 8096},
            
            # Web applications
            "wordpress": {"80/tcp": 8080},
            "ghost": {"2368/tcp": 2368},
            "gitea": {"3000/tcp": 3000, "22/tcp": 2222},
            "nextcloud": {"80/tcp": 8080},
            
            # Admin interfaces
            "phpmyadmin": {"80/tcp": 8080},
            "adminer": {"8080/tcp": 8080},
            "portainer": {"9000/tcp": 9000, "8000/tcp": 8000},
            
            # Development environments
            "code-server": {"8080/tcp": 8080},
            
            # Storage solutions
            "minio": {"9000/tcp": 9000, "9001/tcp": 9001},
        }
        
        # Check for known images
        if base_name in default_ports:
            logger.info(f"Using default port mappings for {image_name}: {default_ports[base_name]}")
            return default_ports[base_name]
            
        # Check for partial image name matches
        for image_type, ports in default_ports.items():
            if image_type in base_name:
                logger.info(f"Using default port mappings based on partial match: {image_type} in {image_name}")
                return ports
                
        # For unknown images without detected ports, guess based on common ports for the type
        # For web server images, default to port 80 if we can't identify the specific type
        if any(term in image_lower for term in ["web", "http", "www"]):
            logger.info(f"Using web server defaults for {image_name}")
            return {"80/tcp": 8080}
            
        # For unknown images, we'll return an empty dict and log a warning
        logger.warning(f"No default port mappings found for image: {image_name}")
        return {}

    def list_running_containers(self) -> List[Dict]:
        """
        List all running containers with their details
        """
        try:
            # Get container list first
            success, output, _ = self._run_docker_command([
                "ps", 
                "--format", "{{json .}}"
            ])
            
            if not success or not output:
                logger.error("Failed to list containers or no containers found")
                return []
            
            # Process each line as a JSON object
            containers = []
            for line in output.strip().split("\n"):
                if not line.strip():
                    continue
                    
                try:
                    container_data = json.loads(line)
                    
                    # Skip frontend and backend containers
                    container_name = container_data.get("Names", "")
                    if "docker-gpt-frontend" in container_name or "docker-gpt-backend" in container_name:
                        logger.debug(f"Skipping system container: {container_name}")
                        continue
                    
                    # Extract and format ports from the Ports field
                    ports_dict = {}
                    ports_str = container_data.get("Ports", "")
                    
                    if ports_str:
                        # Try to parse ports in format like "0.0.0.0:8000->8000/tcp"
                        for port_mapping in ports_str.split(", "):
                            if "->" in port_mapping:
                                host_part, container_part = port_mapping.split("->")
                                
                                # Extract the port number from host part (e.g., "0.0.0.0:8000" -> "8000")
                                if ":" in host_part:
                                    host_port = host_part.split(":")[-1]
                                else:
                                    host_port = host_part
                                
                                # Extract container port and protocol (e.g., "8000/tcp" -> "8000", "tcp")
                                if "/" in container_part:
                                    container_port, protocol = container_part.split("/")
                                    key = f"{container_port}/{protocol}"
                                else:
                                    key = container_port
                                
                                ports_dict[key] = int(host_port) if host_port.isdigit() else host_port
                    
                    # Create a container object with our desired format
                    containers.append({
                        "id": container_data.get("ID", "")[:12],
                        "name": container_data.get("Names", ""),
                        "image": container_data.get("Image", ""),
                        "status": container_data.get("Status", ""),
                        "ports": ports_dict  # Always a dictionary
                    })
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parsing container JSON: {str(e)} - Line: {line}")
                except Exception as e:
                    logger.warning(f"Error processing container data: {str(e)}")
            
            logger.info(f"Found {len(containers)} running containers (excluding system containers)")
            return containers
        except Exception as e:
            logger.error(f"Error listing containers: {str(e)}")
            return []

    def stop_container(self, container_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Stop a running container
        """
        try:
            success, output, stderr = self._run_docker_command(["stop", container_id])
            if success:
                return True, f"Container {container_id[:12]} stopped successfully", None
            else:
                error_msg = f"Error stopping container {container_id}: {output}"
                logger.error(error_msg)
                return False, error_msg, {
                    "command_output": output,
                    "stderr": stderr,
                    "container_id": container_id
                }
        except Exception as e:
            error_msg = f"Error stopping container {container_id}: {str(e)}"
            logger.error(error_msg)
            logger.exception("Exception details:")
            return False, error_msg, {
                "exception": str(e),
                "container_id": container_id,
                "traceback": traceback.format_exc()
            }

    def remove_container(self, container_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Remove a container (whether running or stopped)
        """
        try:
            # First try to stop it if it's running
            self._run_docker_command(["stop", container_id])
            
            # Then remove the container
            success, output, stderr = self._run_docker_command(["rm", container_id])
            if success:
                return True, f"Container {container_id[:12]} removed successfully", None
            else:
                error_msg = f"Error removing container {container_id}: {output}"
                logger.error(error_msg)
                return False, error_msg, {
                    "command_output": output,
                    "stderr": stderr,
                    "container_id": container_id
                }
        except Exception as e:
            error_msg = f"Error removing container {container_id}: {str(e)}"
            logger.error(error_msg)
            logger.exception("Exception details:")
            return False, error_msg, {
                "exception": str(e),
                "container_id": container_id,
                "traceback": traceback.format_exc()
            }

    def list_images(self) -> List[Dict]:
        """
        List all Docker images on the system
        """
        try:
            success, output, _ = self._run_docker_command([
                "images", 
                "--format", "{{json .}}"
            ])
            
            if not success or not output:
                logger.error("Failed to list images or no images found")
                return []
            
            # Process each line as a JSON object
            images = []
            for line in output.strip().split("\n"):
                if not line.strip():
                    continue
                    
                try:
                    image_data = json.loads(line)
                    
                    # Skip system images
                    repository = image_data.get("Repository", "")
                    if repository in ["docker-gpt-frontend", "docker-gpt-backend"]:
                        logger.debug(f"Skipping system image: {repository}")
                        continue
                    
                    # Create an image object with our desired format
                    images.append({
                        "id": image_data.get("ID", "")[:12],
                        "repository": image_data.get("Repository", ""),
                        "tag": image_data.get("Tag", ""),
                        "size": image_data.get("Size", ""),
                        "created": image_data.get("CreatedAt", "")
                    })
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parsing image JSON: {str(e)} - Line: {line}")
                except Exception as e:
                    logger.warning(f"Error processing image data: {str(e)}")
            
            logger.info(f"Found {len(images)} images (excluding system images)")
            return images
        except Exception as e:
            logger.error(f"Error listing images: {str(e)}")
            return []

    def remove_image(self, image_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Remove a Docker image
        
        Returns:
            A tuple of (success, message, error_details)
            - success: Boolean indicating success
            - message: Human-readable message
            - error_details: Detailed error information for debugging (if error occurred)
        """
        try:
            # Remove the image (force it to remove associated containers)
            success, output, stderr = self._run_docker_command(["rmi", "-f", image_id])
            if success:
                return True, f"Image {image_id[:12]} removed successfully", None
            else:
                error_msg = f"Error removing image {image_id}: {output}"
                logger.error(error_msg)
                return False, error_msg, {
                    "command_output": output,
                    "stderr": stderr,
                    "image_id": image_id
                }
        except Exception as e:
            error_msg = f"Error removing image {image_id}: {str(e)}"
            logger.error(error_msg)
            logger.exception("Exception details:")
            return False, error_msg, {
                "exception": str(e),
                "image_id": image_id,
                "traceback": traceback.format_exc()
            }

    def verify_image_exists(self, image_name: str) -> Tuple[bool, str, Dict]:
        """
        Verify if a Docker image exists locally or can be pulled from registry
        
        Returns:
            Tuple containing:
            - Boolean indicating if image exists or can be pulled
            - Message about the verification status
            - Dictionary with detailed information about the verification process
        """
        verification_details = {
            "image": image_name,
            "timestamp": datetime.now().isoformat(),
            "steps": []
        }
        
        try:
            # Step 1: Check if the image exists locally
            verification_details["steps"].append("Checking if image exists locally")
            local_cmd = ["images", "--format", "{{.Repository}}:{{.Tag}}", image_name]
            local_success, local_output, _ = self._run_docker_command(local_cmd)
            
            if local_success and local_output.strip():
                verification_details["steps"].append(f"Image found locally: {local_output.strip()}")
                verification_details["exists_locally"] = True
                return True, f"Image '{image_name}' exists locally", verification_details
            
            # Step 2: Check if the image can be pulled from registry
            # First, check if image format is valid
            if ':' not in image_name and not image_name.startswith('sha256:'):
                # Append :latest tag if no tag is specified
                original_name = image_name
                image_name = f"{image_name}:latest"
                verification_details["steps"].append(f"No tag specified, using '{image_name}'")
                verification_details["original_name"] = original_name
            
            # Instead of pulling the full image, just check if it exists on Docker Hub
            # We can do this with docker manifest inspect
            verification_details["steps"].append(f"Checking if image '{image_name}' exists in registry")
            manifest_cmd = ["manifest", "inspect", image_name]
            manifest_success, manifest_output, manifest_error = self._run_docker_command(manifest_cmd)
            
            if manifest_success:
                verification_details["steps"].append("Image found in registry")
                verification_details["exists_in_registry"] = True
                return True, f"Image '{image_name}' exists in registry", verification_details
            else:
                # Docker manifest inspect might fail for various reasons unrelated to image existence
                # Let's check if it's a permission issue or network issue
                verification_details["steps"].append("Registry check failed, attempting fallback methods")
                
                # Try Docker Hub API for official images
                if '/' not in image_name:
                    verification_details["steps"].append("Checking official image in Docker Hub")
                    return False, f"Image '{image_name}' not found or not accessible", verification_details
                
                # If all checks fail, report failure
                verification_details["steps"].append("All verification methods failed")
                verification_details["exists_locally"] = False
                verification_details["exists_in_registry"] = False
                verification_details["error"] = manifest_output if manifest_output else "Unknown error"
                return False, f"Image '{image_name}' not found or not accessible", verification_details
                
        except Exception as e:
            logger.error(f"Error verifying image '{image_name}': {str(e)}")
            logger.exception("Image verification exception:")
            verification_details["steps"].append(f"Error during verification: {str(e)}")
            verification_details["error"] = str(e)
            verification_details["traceback"] = traceback.format_exc()
            return False, f"Error verifying image '{image_name}': {str(e)}", verification_details
            
    def suggest_alternative_images(self, failed_image: str) -> List[Dict]:
        """
        Suggest alternative images when a requested image fails
        """
        suggestions = []
        
        # Extract base name if it has a path
        base_name = failed_image.split('/')[-1].split(':')[0]
        
        # Extract keywords from the image name
        keywords = []
        # Break camelCase and hyphenated names
        import re
        words = re.findall(r'[A-Za-z][a-z]*', base_name)
        keywords.extend([w.lower() for w in words if len(w) > 2])
        
        # Add hyphenated parts
        if '-' in base_name:
            keywords.extend([p.lower() for p in base_name.split('-') if len(p) > 2])
            
        logger.info(f"Extracted keywords from failed image: {keywords}")
        
        # Create mapping of common alternatives
        alternatives = {
            "sql": ["mysql", "postgres", "mariadb"],
            "mssql": ["mcr.microsoft.com/mssql/server"],
            "microsoft": ["mcr.microsoft.com/mssql/server"],
            "mongo": ["mongo", "mongodb"],
            "node": ["node"],
            "python": ["python"],
            "web": ["nginx", "httpd"],
            "redis": ["redis"],
            "cache": ["redis", "memcached"],
            "database": ["mysql", "postgres", "mariadb"],
            "db": ["mysql", "postgres"],
        }
        
        # Find alternatives based on keywords
        for keyword in keywords:
            if keyword in alternatives:
                for alt in alternatives[keyword]:
                    # Verify the alternative exists before suggesting it
                    exists, _, details = self.verify_image_exists(alt)
                    if exists:
                        suggestions.append({
                            "name": alt,
                            "reason": f"Alternative to '{failed_image}' based on keyword '{keyword}'",
                            "verified": True
                        })
        
        # If no alternatives found, suggest some common images
        if not suggestions:
            default_options = ["nginx", "ubuntu", "alpine"]
            for option in default_options:
                exists, _, details = self.verify_image_exists(option)
                if exists:
                    suggestions.append({
                        "name": option,
                        "reason": f"Common alternative when no specific match found for '{failed_image}'",
                        "verified": True
                    })
        
        return suggestions[:3]  # Return top 3 alternatives 

    def update_container_config(self, container_id: str, config_path: str, updates: Dict) -> Tuple[bool, str, Dict]:
        """
        Update configuration files inside a running container
        
        Args:
            container_id: The ID of the container
            config_path: Path to the configuration file inside the container
            updates: Dictionary of key-value pairs to update in the config
            
        Returns:
            Tuple containing:
            - Success status
            - Message
            - Dictionary with detailed logs
        """
        logs = {
            "steps": [],
            "container_id": container_id,
            "config_path": config_path,
            "updates": updates,
            "timestamp": datetime.now().isoformat(),
            "success": False
        }
        
        try:
            # First check if the container is running
            log_msg = f"Checking if container {container_id} is running"
            logger.info(log_msg)
            logs["steps"].append(log_msg)
            
            inspect_cmd = ["container", "inspect", container_id]
            success, output, parsed = self._run_docker_command(inspect_cmd)
            
            if not success or not parsed:
                error_msg = f"Failed to inspect container {container_id}"
                logger.error(error_msg)
                logs["steps"].append(error_msg)
                logs["error"] = "CONTAINER_NOT_FOUND"
                return False, error_msg, logs
            
            container_state = parsed[0].get("State", {})
            if not container_state.get("Running", False):
                error_msg = f"Container {container_id} is not running"
                logger.error(error_msg)
                logs["steps"].append(error_msg)
                logs["error"] = "CONTAINER_NOT_RUNNING"
                return False, error_msg, logs
            
            # Check if the config file exists
            log_msg = f"Checking if config file {config_path} exists in container"
            logger.info(log_msg)
            logs["steps"].append(log_msg)
            
            file_check_cmd = ["exec", container_id, "sh", "-c", f"test -f {config_path} && echo 'exists' || echo 'not found'"]
            success, output, _ = self._run_docker_command(file_check_cmd)
            
            if not success or "not found" in output:
                error_msg = f"Config file {config_path} not found in container {container_id}"
                logger.error(error_msg)
                logs["steps"].append(error_msg)
                logs["error"] = "CONFIG_FILE_NOT_FOUND"
                return False, error_msg, logs
            
            # Read the current config
            log_msg = f"Reading current config from {config_path}"
            logger.info(log_msg)
            logs["steps"].append(log_msg)
            
            read_cmd = ["exec", container_id, "cat", config_path]
            success, output, _ = self._run_docker_command(read_cmd)
            
            if not success:
                error_msg = f"Failed to read config file {config_path}"
                logger.error(error_msg)
                logs["steps"].append(error_msg)
                logs["error"] = "CONFIG_READ_ERROR"
                return False, error_msg, logs
            
            # Parse the config
            try:
                current_config = json.loads(output)
                logs["original_config"] = current_config
            except json.JSONDecodeError:
                # If it's not JSON, try to handle as a text file with key=value pairs
                try:
                    current_config = {}
                    for line in output.strip().split("\n"):
                        if "=" in line and not line.strip().startswith("#"):
                            key, value = line.split("=", 1)
                            current_config[key.strip()] = value.strip()
                    logs["original_config"] = current_config
                except Exception:
                    error_msg = f"Failed to parse config file {config_path}, not a valid JSON or key=value format"
                    logger.error(error_msg)
                    logs["steps"].append(error_msg)
                    logs["error"] = "CONFIG_PARSE_ERROR"
                    return False, error_msg, logs
            
            # Update the config
            log_msg = f"Updating config with {len(updates)} changes"
            logger.info(log_msg)
            logs["steps"].append(log_msg)
            
            # Deep merge of nested dictionaries
            def deep_update(d, u):
                for k, v in u.items():
                    if isinstance(v, dict) and isinstance(d.get(k), dict):
                        deep_update(d[k], v)
                    else:
                        d[k] = v
            
            try:
                # Make a copy of the original config
                updated_config = current_config.copy() if isinstance(current_config, dict) else {}
                
                # Apply updates
                deep_update(updated_config, updates)
                logs["updated_config"] = updated_config
                
                # Convert back to JSON or appropriate format
                if isinstance(current_config, dict):
                    config_str = json.dumps(updated_config, indent=2)
                else:
                    # Handle key=value format
                    config_lines = []
                    for k, v in updated_config.items():
                        config_lines.append(f"{k}={v}")
                    config_str = "\n".join(config_lines)
                
                # Write updated config to a temporary file
                temp_file = f"/tmp/updated_config_{container_id}.json"
                with open(temp_file, "w") as f:
                    f.write(config_str)
                
                # Copy the temp file to the container
                copy_cmd = ["cp", temp_file, f"{container_id}:{config_path}"]
                success, output, _ = self._run_docker_command(copy_cmd)
                
                if not success:
                    error_msg = f"Failed to write updated config to {config_path}"
                    logger.error(error_msg)
                    logs["steps"].append(error_msg)
                    logs["error"] = "CONFIG_WRITE_ERROR"
                    return False, error_msg, logs
                
                # Remove the temp file
                os.remove(temp_file)
                
                # Restart the container to apply changes if needed
                log_msg = "Restarting container to apply configuration changes"
                logger.info(log_msg)
                logs["steps"].append(log_msg)
                
                restart_cmd = ["restart", container_id]
                success, output, _ = self._run_docker_command(restart_cmd)
                
                if not success:
                    error_msg = f"Failed to restart container {container_id}"
                    logger.error(error_msg)
                    logs["steps"].append(error_msg)
                    logs["error"] = "RESTART_ERROR"
                    return False, error_msg, logs
                
                logs["success"] = True
                success_msg = f"Successfully updated configuration for container {container_id}"
                logs["steps"].append(success_msg)
                return True, success_msg, logs
                
            except Exception as e:
                error_msg = f"Error updating config: {str(e)}"
                logger.error(error_msg)
                logger.exception("Config update exception details:")
                logs["steps"].append(error_msg)
                logs["error"] = "UPDATE_ERROR"
                logs["error_details"] = {
                    "exception": str(e),
                    "traceback": traceback.format_exc()
                }
                return False, error_msg, logs
                
        except Exception as e:
            error_msg = f"Error updating container config: {str(e)}"
            logger.error(error_msg)
            logger.exception("Container config update exception details:")
            logs["steps"].append(error_msg)
            logs["error"] = "GENERAL_ERROR"
            logs["error_details"] = {
                "exception": str(e),
                "traceback": traceback.format_exc()
            }
            return False, error_msg, logs 