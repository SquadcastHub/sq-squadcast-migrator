"""Schedule resource client."""

from typing import List, Dict, Any

from .base import BaseResource
from ..models.schedule import OpsGenieSchedule


class SchedulesClient(BaseResource[OpsGenieSchedule]):
    """Client for schedule operations."""

    def __init__(self, http_client):
        """Initialize schedules client."""
        super().__init__(http_client, OpsGenieSchedule)

    def list_schedules(self, expand: bool = True) -> List[OpsGenieSchedule]:
        """
        Get all schedules.

        Args:
            expand: Whether to include rotations in response (default: True)

        Returns:
            List of OpsGenieSchedule objects
        """
        params = {"sort": "name", "order": "ASC"}
        if expand:
            params["expand"] = "rotation"

        return self._get_all("schedules", params=params)

    def get_schedule(self, schedule_id: str, expand: bool = True) -> OpsGenieSchedule:
        """
        Get a specific schedule by ID.

        Args:
            schedule_id: ID of the schedule to retrieve
            expand: Whether to include rotations in response (default: True)

        Returns:
            OpsGenieSchedule object with complete details including rotations
        """
        params = {"expand": "rotation"} if expand else None
        return self._get_single(f"schedules/{schedule_id}", params=params)

    def list_timeline(
        self, schedule_id: str, interval_start: str, interval_end: str
    ) -> List[Dict[str, Any]]:
        """
        Get timeline of a schedule.

        Args:
            schedule_id: ID of the schedule
            interval_start: Start of timeline interval (ISO8601 format)
            interval_end: End of timeline interval (ISO8601 format)

        Returns:
            List of timeline entries
        """
        params = {
            "scheduleId": schedule_id,
            "intervalStart": interval_start,
            "intervalEnd": interval_end,
        }
        response = self.http.request(
            "GET", f"schedules/{schedule_id}/timeline", params=params
        )
        return response.get("data", {}).get("timeline", [])
