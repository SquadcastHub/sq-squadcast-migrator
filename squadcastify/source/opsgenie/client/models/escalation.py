"""Escalation policy models for OpsGenie API."""

from dataclasses import dataclass, field
from typing import List, Optional

from .base import OpsGenieModel


@dataclass
class OpsGenieEscalationRule(OpsGenieModel):
    """Rule in an escalation policy."""

    condition: str  # e.g., "if-not-acked"
    notify_type: str  # e.g., "user", "team", "schedule"
    recipient: str
    delay: Optional[int] = None  # Delay in minutes
    enabled: bool = True


@dataclass
class OpsGenieEscalationPolicy(OpsGenieModel):
    """Represents an escalation policy in OpsGenie."""

    name: str
    description: Optional[str] = None
    rules: List[OpsGenieEscalationRule] = field(default_factory=list)
    repeat: Optional[dict] = None
    owner_team: Optional[dict] = None
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "OpsGenieEscalationPolicy":
        """Create an escalation policy from API response data."""
        rules = [
            OpsGenieEscalationRule(
                id=rule.get("id", ""),
                condition=rule.get("condition", ""),
                notify_type=rule.get("notifyType", ""),
                recipient=rule.get("recipient", {}).get("id", ""),
                delay=rule.get("delay", None),
                enabled=rule.get("enabled", True),
            )
            for rule in data.get("rules", [])
        ]

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            rules=rules,
            repeat=data.get("repeat"),
            owner_team=data.get("ownerTeam"),
            enabled=data.get("enabled", True),
        )
