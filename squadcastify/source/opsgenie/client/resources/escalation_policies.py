"""Escalation policy resource client."""

from typing import List

from .base import BaseResource
from ..models.escalation import OpsGenieEscalationPolicy


class EscalationPoliciesClient(BaseResource[OpsGenieEscalationPolicy]):
    """Client for escalation policy operations."""

    def __init__(self, http_client):
        """Initialize escalation policies client."""
        super().__init__(http_client, OpsGenieEscalationPolicy)

    def list_policies(self) -> List[OpsGenieEscalationPolicy]:
        """
        Get all escalation policies.

        Returns:
            List of OpsGenieEscalationPolicy objects
        """
        params = {"sort": "name", "order": "ASC"}
        return self._get_all("escalations", params=params)

    def get_policy(self, policy_id: str) -> OpsGenieEscalationPolicy:
        """
        Get a specific escalation policy by ID.

        Args:
            policy_id: ID of the policy to retrieve

        Returns:
            OpsGenieEscalationPolicy object with rules and details
        """
        return self._get_single(f"escalations/{policy_id}")
