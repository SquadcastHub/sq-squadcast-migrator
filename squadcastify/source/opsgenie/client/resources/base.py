"""Base resource client."""

from typing import TypeVar, Type, Dict, Any, Optional, List, Generic
from ..http import HTTPClient
from ..models.base import OpsGenieModel

T = TypeVar("T", bound=OpsGenieModel)


class BaseResource(Generic[T]):
    """Base class for all resource clients."""

    def __init__(self, http_client: HTTPClient, model_class: Type[T]):
        """
        Initialize resource client.

        Args:
            http_client: HTTP client for making API requests
            model_class: Class to use for creating resource instances
        """
        self.http = http_client
        self.model_class = model_class

    def _create_model(self, data: Dict[str, Any]) -> T:
        """
        Create a model instance from API response data.

        Args:
            data: Dictionary containing model data

        Returns:
            Instance of the model
        """
        return self.model_class.from_dict(data)

    def _get_all(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """
        Get all resources by handling pagination automatically.

        Args:
            endpoint: API endpoint
            params: Optional query parameters

        Returns:
            List of resource models
        """
        all_items = []
        limit = 100
        offset = 0

        while True:
            request_params = {"limit": limit, "offset": offset}
            if params:
                request_params.update(params)

            response = self.http.request("GET", endpoint, params=request_params)
            items = response.get("data", [])

            if not items:
                break

            all_items.extend(self._create_model(item) for item in items)

            if len(items) < limit:
                break

            offset += limit

        return all_items

    def _get_single(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> T:
        """
        Get a single resource.

        Args:
            endpoint: API endpoint
            params: Optional query parameters

        Returns:
            Resource model
        """
        response = self.http.request("GET", endpoint, params=params)
        return self._create_model(response["data"])
