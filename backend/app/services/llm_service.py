import openai
import os
import json
from typing import Dict, List, Tuple, Optional
import numpy as np
from app.core.config import settings
from app.utils.logger import logger

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("No OpenAI API key provided. LLM features will not work properly.")
        else:
            logger.info("OpenAI API key configured")
            
        openai.api_key = self.api_key
        self.cache_file = "docker_images_cache.json"
        self._load_cache()
    
    def _load_cache(self):
        """Load cached Docker image metadata if available"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.image_cache = json.load(f)
            else:
                self.image_cache = []
        except Exception as e:
            logger.error(f"Error loading image cache: {str(e)}")
            self.image_cache = []
    
    def _save_cache(self):
        """Save Docker image metadata to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.image_cache, f)
        except Exception as e:
            logger.error(f"Error saving image cache: {str(e)}")
    
    def update_cache(self, images: List[Dict]):
        """Update the cache with new images"""
        # Simple implementation - replace with more sophisticated caching if needed
        self.image_cache = images
        self._save_cache()
    
    async def process_prompt(self, prompt: str) -> Dict:
        """
        Process user prompt and select appropriate Docker image
        
        Returns a dictionary with:
        - image: The name of the Docker image to use
        - description: A description of the selected image
        - stars: The popularity rating of the image
        - error: Optional error information if something went wrong
        """
        try:
            if not self.api_key:
                logger.warning("No OpenAI API key configured. Using fallback image selection.")
                # Provide a direct fallback without trying to call OpenAI
                fallback_images = {
                    "sql": {"image": "mysql", "description": "MySQL is a widely used relational database", "stars": 10000},
                    "mysql": {"image": "mysql", "description": "MySQL database server", "stars": 10000},
                    "postgres": {"image": "postgres", "description": "PostgreSQL database", "stars": 10000},
                    "postgresql": {"image": "postgres", "description": "PostgreSQL database", "stars": 10000},
                    "mssql": {"image": "mcr.microsoft.com/mssql/server", "description": "Microsoft SQL Server", "stars": 5000},
                    "microsoft sql": {"image": "mcr.microsoft.com/mssql/server", "description": "Microsoft SQL Server", "stars": 5000},
                    "web": {"image": "nginx", "description": "Nginx web server", "stars": 10000},
                    "python": {"image": "python", "description": "Python programming language environment", "stars": 10000},
                    "node": {"image": "node", "description": "Node.js JavaScript runtime", "stars": 10000},
                    "database": {"image": "postgres", "description": "PostgreSQL database", "stars": 10000},
                    "mongo": {"image": "mongo", "description": "MongoDB NoSQL database", "stars": 10000},
                    "redis": {"image": "redis", "description": "Redis in-memory data store", "stars": 10000}
                }
                
                # Simple keyword matching for fallback
                prompt_lower = prompt.lower()
                for keyword, image_info in fallback_images.items():
                    if keyword in prompt_lower:
                        return image_info
                
                # Default fallback
                return {
                    "image": "nginx",
                    "description": "Fallback Nginx web server (No OpenAI API key configured)",
                    "stars": 10000
                }
            
            logger.info(f"Processing prompt: {prompt}")
            
            # Attempt to use OpenAI to analyze the prompt
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI that selects the most appropriate Docker image based on a user's requirements."},
                        {"role": "user", "content": f"Based on this requirement: '{prompt}', suggest the best Docker image to use. Respond ONLY with a JSON object containing these fields: 'image' (the Docker image name), 'description' (a brief description), and 'stars' (a number representing popularity)."}
                    ],
                    temperature=0.3,
                    max_tokens=100
                )
                
                # Parse the response
                result = response.choices[0].message.content
                logger.info(f"OpenAI response: {result}")
                
                # Sometimes the model includes markdown code blocks or extra text
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0].strip()
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0].strip()
                
                # Parse the JSON
                try:
                    parsed = json.loads(result)
                    return {
                        "image": self._sanitize_image_name(parsed.get("image", "nginx")),
                        "description": parsed.get("description", "Automatically selected based on your requirements"),
                        "stars": parsed.get("stars", 10000)
                    }
                except json.JSONDecodeError as json_err:
                    logger.error(f"Failed to parse OpenAI response as JSON: {json_err}")
                    logger.error(f"Raw response: {result}")
                    # Use fallback instead of raising error
                    logger.warning("Using fallback image due to JSON parse error")
                    return {
                        "image": "nginx",
                        "description": f"Fallback (JSON parsing error): {result[:50]}...",
                        "stars": 10000
                    }
                    
            except Exception as openai_err:
                logger.error(f"OpenAI API error: {str(openai_err)}")
                # Use fallback instead of raising error
                logger.warning("Using fallback image due to OpenAI API error")
                return {
                    "image": "nginx",
                    "description": f"Fallback (API error): {str(openai_err)[:50]}...",
                    "stars": 10000
                }
                
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"Error in process_prompt: {error_type} - {error_msg}")
            # Use fallback instead of raising error
            return {
                "image": "nginx",
                "description": f"Fallback deployment (Error: {error_type})",
                "stars": 10000
            }
    
    def _extract_keywords(self, prompt: str) -> List[str]:
        """Extract keywords from prompt for Docker Hub search"""
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract 3-5 keywords for searching Docker Hub images based on the user's request."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            keywords_text = response.choices[0].message.content
            # Simple parsing - in production, make this more robust
            keywords = [k.strip() for k in keywords_text.split(',')]
            return keywords
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            # Fallback to simple word extraction
            return [w for w in prompt.lower().split() if len(w) > 3]
    
    def _extract_image_from_response(self, llm_response: str, available_images: List[Dict]) -> Dict:
        """Extract the selected image from LLM response"""
        # This is a simple implementation - in production, make this more robust
        for image in available_images:
            if image['name'] in llm_response:
                return image
        
        # If no match found, return the first available image or an empty dict
        return available_images[0] if available_images else {}
    
    def _generate_container_config(self, prompt: str, selected_image: Dict) -> Dict:
        """Generate container configuration based on prompt and selected image"""
        try:
            # Default configs for common image types
            image_name = selected_image.get('name', '').lower()
            
            # Basic configurations for common image types
            config = {
                "ports": {},
                "environment": {}
            }
            
            # Web servers typically use port 80
            if any(server in image_name for server in ['nginx', 'httpd', 'apache', 'web']):
                config["ports"] = {"80/tcp": 8080}
                
            # Jupyter notebooks typically use port 8888
            elif 'jupyter' in image_name:
                config["ports"] = {"8888/tcp": 8888}
            
            # Node.js applications typically use port 3000
            elif 'node' in image_name:
                config["ports"] = {"3000/tcp": 3000}
            
            # Microsoft SQL Server typically uses port 1433
            elif 'mssql' in image_name or ('microsoft' in image_name and 'sql' in image_name):
                config["ports"] = {"1433/tcp": 1433}
                config["environment"] = {
                    "ACCEPT_EULA": "Y",
                    "SA_PASSWORD": "StrongP@ssw0rd!",  # Strong password required for SQL Server
                    "MSSQL_PID": "Express"  # Using Express edition
                }
                
            # PostgreSQL typically uses port 5432
            elif 'postgres' in image_name:
                config["ports"] = {"5432/tcp": 5432}
                config["environment"] = {"POSTGRES_PASSWORD": "password"}
            
            # MySQL typically uses port 3306
            elif 'mysql' in image_name:
                config["ports"] = {"3306/tcp": 3306}
                config["environment"] = {"MYSQL_ROOT_PASSWORD": "password"}
            
            # MongoDB typically uses port 27017
            elif 'mongo' in image_name:
                config["ports"] = {"27017/tcp": 27017}
            
            # Redis typically uses port 6379
            elif 'redis' in image_name:
                config["ports"] = {"6379/tcp": 6379}
            
            # Tomcat typically uses port 8080
            elif 'tomcat' in image_name:
                config["ports"] = {"8080/tcp": 8080}
            
            # Elasticsearch typically uses ports 9200 and 9300
            elif 'elastic' in image_name:
                config["ports"] = {"9200/tcp": 9200, "9300/tcp": 9300}
            
            # RabbitMQ typically uses ports 5672 and 15672
            elif 'rabbit' in image_name:
                config["ports"] = {"5672/tcp": 5672, "15672/tcp": 15672}
            
            # Jellyfin media server uses ports 8096 (API) and 80 (web)
            elif 'jellyfin' in image_name:
                config["ports"] = {"8096/tcp": 8096, "80/tcp": 8080}
                logger.info(f"Detected Jellyfin media server. Mapping both ports 8096 and 80.")
                
            # For all other images, default to port 80 if it might be a web service
            elif any(term in prompt.lower() for term in ['web', 'http', 'website', 'server']):
                config["ports"] = {"80/tcp": 8080}
                logger.info(f"No specific port config for {image_name}, but prompt suggests web service. Using port 80->8080")
            
            # Ask LLM for more specific configuration if needed
            if not config["ports"] and not config["environment"]:
                logger.warning(f"No default configuration found for {image_name}. Generating generic config.")
                # Default to port 80->8080 as a safe fallback for many services
                config["ports"] = {"80/tcp": 8080}
                
            return config
            
        except Exception as e:
            logger.error(f"Error generating container config: {str(e)}")
            # Return a safe default with port 80 mapped
            return {"ports": {"80/tcp": 8080}, "environment": {}}
    
    def _fallback_image_selection(self, prompt: str, available_images: List[Dict]) -> Dict:
        """Fallback method for image selection when LLM fails"""
        prompt_lower = prompt.lower()
        
        # Simple keyword matching
        for image in available_images:
            name_lower = image['name'].lower()
            
            # Check for exact matches first
            if name_lower in prompt_lower:
                return image
        
        # If no exact match, try partial matches
        for keyword in prompt_lower.split():
            if len(keyword) < 4:  # Skip short words
                continue
                
            for image in available_images:
                if keyword in image['name'].lower() or keyword in image.get('description', '').lower():
                    return image
        
        # If all else fails, return the first image or an empty dict
        return available_images[0] if available_images else {}
    
    def _sanitize_image_name(self, image_name: str) -> str:
        """
        Sanitize and correct Docker image names to ensure they exist and can be pulled
        Pattern-based corrections instead of hardcoded mappings
        """
        if not image_name or len(image_name.strip()) == 0:
            logger.warning("Empty image name provided, using nginx as fallback")
            return "nginx"
            
        # Remove any unnecessary whitespace or quotes
        image_name = image_name.strip().strip('"\'')
        
        # Common patterns and corrections
        patterns = [
            # Microsoft SQL Server pattern - multiple variants to one standard
            {
                "pattern": lambda img: ("microsoft" in img.lower() and "sql" in img.lower() and "/mssql/" not in img.lower()),
                "replacement": "mcr.microsoft.com/mssql/server",
                "reason": "Converting to official Microsoft SQL Server container registry path"
            },
            # Missing latest tag for images that require it
            {
                "pattern": lambda img: any(img == name for name in ["mongo-express", "adminer", "phpmyadmin"]),
                "replacement": lambda img: f"{img}:latest",
                "reason": "Adding :latest tag which is required for this image"
            },
            # PostgreSQL variants
            {
                "pattern": lambda img: img.lower() in ["postgresql", "postgres-server"],
                "replacement": "postgres",
                "reason": "Standardizing PostgreSQL image name"
            },
            # MariaDB variants
            {
                "pattern": lambda img: img.lower() in ["mariadb-server", "maria-db"],
                "replacement": "mariadb",
                "reason": "Standardizing MariaDB image name"
            }
        ]
        
        # Apply patterns
        for pattern_data in patterns:
            pattern_func = pattern_data["pattern"]
            if pattern_func(image_name):
                replacement = pattern_data["replacement"]
                reason = pattern_data["reason"]
                
                # Handle function-based replacements
                if callable(replacement):
                    corrected_name = replacement(image_name)
                else:
                    corrected_name = replacement
                    
                logger.warning(f"Correcting image name from '{image_name}' to '{corrected_name}': {reason}")
                return corrected_name
                
        # Handle legacy registry references
        if '/' in image_name and not (
            image_name.startswith('docker.io/') or 
            image_name.startswith('mcr.microsoft.com/') or
            '.' in image_name.split('/')[0]
        ):
            # Might be legacy format, check if it's a potential Microsoft image
            parts = image_name.split('/')
            if parts[0] == "microsoft":
                logger.warning(f"Detected legacy Microsoft registry reference: {image_name}")
                # Try to correct based on image type
                if "mssql" in parts[1]:
                    corrected = "mcr.microsoft.com/mssql/server"
                    logger.warning(f"Correcting to {corrected}")
                    return corrected
        
        # If no corrections needed, return the original
        return image_name 