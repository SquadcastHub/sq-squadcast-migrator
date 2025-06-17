"""Base model for OpsGenie resources."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OpsGenieModel:
    """Base model for all OpsGenie resources."""

    id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpsGenieModel":
        """
        Create a model instance from a dictionary.

        Args:
            data: Dictionary containing model data

        Returns:
            Instance of the model
        """
        # Filter out None values and unknown fields
        valid_fields = {
            k: v for k, v in data.items() if v is not None and k in cls.__annotations__
        }
        return cls(**valid_fields)
