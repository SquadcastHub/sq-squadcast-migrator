import requests
from typing import Dict, List, Any, Optional
import logging
from config.config import settings

logger = logging.getLogger(__name__)

class OpsGenieClient:
    """Client for the OpsGenie API."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initialize OpsGenie client.
        
        Args:
            api_key: OpsGenie API key. If not provided, will use from settings.
            api_url: OpsGenie API URL. If not provided, will use from settings.
        """
        self.api_key = api_key or settings.opsgenie_api_key
        self.api_url = api_url or settings.opsgenie_api_url
        self.headers = {
            "Authorization": f"GenieKey {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            logger.error("OpsGenie API key not provided")
            raise ValueError("OpsGenie API key is required")
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, json_data: Dict = None) -> Dict:
        url = f"{self.api_url}/{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=json_data
        )
        
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            logger.error(f"Response content: {response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise
    
    # Define methods to interact with OpsGenie API
    def get_users(self) -> List[Dict[str, Any]]:
        logger.info("Fetching users from OpsGenie")
        response = self._make_request("GET", "users")
        return response.get("data", [])
    
    def get_teams(self) -> List[Dict[str, Any]]:
        logger.info("Fetching teams from OpsGenie")
        response = self._make_request("GET", "teams")
        return response.get("data", [])
    # Add more methods as needed