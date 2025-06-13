"""Resource-specific clients for OpsGenie API."""

from .users import UsersClient
from .teams import TeamsClient
from .escalation_policies import EscalationPoliciesClient
from .schedules import SchedulesClient

__all__ = ["UsersClient", "TeamsClient", "EscalationPoliciesClient", "SchedulesClient"]
