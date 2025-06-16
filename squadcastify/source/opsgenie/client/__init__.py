"""OpsGenie API client package."""

from .api import OpsgenieAPIClient
from .models.user import OpsGenieUser
from .models.team import OpsGenieTeam, OpsGenieTeamMember
from .errors import (
    OpsGenieError,
    OpsGenieAPIError,
    OpsGenieNotFoundError,
    OpsGenieAuthenticationError,
    OpsGenieRateLimitError,
    OpsGenieValidationError,
)

__all__ = [
    "OpsgenieAPIClient",
    "OpsGenieUser",
    "OpsGenieTeam",
    "OpsGenieTeamMember",
    "OpsGenieError",
    "OpsGenieAPIError",
    "OpsGenieNotFoundError",
    "OpsGenieAuthenticationError",
    "OpsGenieRateLimitError",
    "OpsGenieValidationError",
]

# Version of the package
__version__ = "0.1.0"
