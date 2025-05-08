from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class AlertingClient(ABC):
    """
    Abstract base class for all alerting system clients.
    This class defines the common interface that all alerting system clients should implement.
    """

    @abstractmethod
    def transform_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a user object from the alerting system to a squadcast format.
        
        Returns:
            Transformed user object.
        """
        pass
    
    @abstractmethod
    def get_users(self) -> List[Dict[str, Any]]:
        """
        Get all users from the alerting system.
        
        Returns:
            List of user objects.
        """
        pass

    @abstractmethod
    def transform_team(self, team: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a team object from the alerting system to a squadcast format.
        
        Returns:
            Transformed team object.
        """
        pass
    
    @abstractmethod
    def get_teams(self) -> List[Dict[str, Any]]:
        """
        Get all teams from the alerting system.
        
        Returns:
            List of team objects.
        """
        pass
    
    @abstractmethod
    def get_escalation_policies(self) -> List[Dict[str, Any]]:
        """
        Get all escalation policies from the alerting system.
        
        Returns:
            List of escalation policy objects.
        """
        pass
    
    @abstractmethod
    def get_schedules(self) -> List[Dict[str, Any]]:
        """
        Get all schedules from the alerting system.
        
        Returns:
            List of schedule objects.
        """
        pass