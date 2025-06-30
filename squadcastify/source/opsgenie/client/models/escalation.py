"""Escalation policy models for OpsGenie API."""

from dataclasses import dataclass, field
from typing import List, Optional

from .base import OpsGenieModel, OpsGenieOwnerTeam


@dataclass
class OpsGenieEscalationRule(OpsGenieModel):
    """Rule in an escalation policy."""

    condition: str  # e.g., "if-not-acked"
    notify_type: str  # e.g., "default", "user", "team", "schedule"
    recipient: str  # ID of the recipient
    recipient_type: Optional[str] = None  # Type of recipient (user, team, schedule)
    delay: Optional[dict] = None  # Delay with timeAmount and timeUnit
    enabled: bool = True

@dataclass
class OpsGenieEscalationRepeat:
    """Repeat configuration for escalation policy rules."""
    waitInterval: int  # Time to wait before repeating in minutes
    count: int  # Number of times to repeat
    resetRecipientStates: bool = False  # Whether to reset recipient states after repeat
    closeAlertAfterAll: bool = False  # Whether to close alert after all repeats

    
@dataclass
class OpsGenieEscalationPolicy(OpsGenieModel):
    """Represents an escalation policy in OpsGenie."""

    name: str
    description: Optional[str] = None
    rules: List[OpsGenieEscalationRule] = field(default_factory=list)
    repeat: Optional[OpsGenieEscalationRepeat] = None
    owner_team: Optional[OpsGenieOwnerTeam] = None
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "OpsGenieEscalationPolicy":
        """Create an escalation policy from API response data."""
        rules = []
        for rule_data in data.get("rules", []):
            # Extract recipient information
            recipient_dict = rule_data.get("recipient", {})
            recipient_id = recipient_dict.get("id", "")
            recipient_type = recipient_dict.get("type", "")
            
            # Create the rule object
            rule = OpsGenieEscalationRule(
                id=rule_data.get("id", ""),
                condition=rule_data.get("condition", ""),
                notify_type=rule_data.get("notifyType", ""),
                recipient=recipient_id,
                recipient_type=recipient_type,
                delay=rule_data.get("delay", None),
                enabled=rule_data.get("enabled", True),
            )
            rules.append(rule)

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            rules=rules,
            repeat=OpsGenieEscalationRepeat(**data.get("repeat", {})) if data.get("repeat") else None,
            owner_team=OpsGenieOwnerTeam(**data.get("ownerTeam", {})) if data.get("ownerTeam") else None,
            enabled=data.get("enabled", True),
        )
