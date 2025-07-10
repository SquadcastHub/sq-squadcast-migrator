"""OpsGenie to Squadcast migrator."""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import traceback
from tqdm import tqdm

from tqdm import tqdm

from squadcastify.source.opsgenie.client.models.escalation import OpsGenieEscalationPolicy
from squadcastify.source.opsgenie.client.models.schedule import OpsGenieSchedule, OpsGenieRotation
from squadcastify.terraform.transformer import Transformer

from .context import MigrationContext
from .client.api import OpsgenieAPIClient
from ...terraform.models import (
    SquadcastTeam,
    SquadcastTeamMember,
    SquadcastUser,
    SquadcastEscalationPolicy,
    SquadcastSchedule,
    ScheduleRotation,
    TerraformResource,
    EntityOwner,
    Target,
    Rule,
    Repeat,
    Participant,
    ParticipantGroup,
    ShiftTimeslot,
    RoundRobin,
    SquadcastSquad,
    SquadMember
)

logger = logging.getLogger(__name__)


@dataclass
class OpsGenieTransformer(Transformer):
    """
    OpsGenieTransformer is responsible for migrating resources from OpsGenie to Terraform configurations.

    This transformer handles the following migration steps:
    - Migrates users from OpsGenie, mapping their details to SquadcastUser resources and tracking them in the migration context.
    - Migrates teams from OpsGenie, mapping their details to SquadcastTeam resources, and associates team members with the corresponding users if they have been migrated.
    - Migrates escalation policies from OpsGenie, mapping their details to SquadcastEscalationPolicy resources.
    - Maintains a MigrationContext to track the mapping between OpsGenie and Squadcast resources for users, teams, and escalation policies.

    Attributes:
        client (OpsgenieAPIClient): The OpsGenie API client used to fetch users and teams.
        context (MigrationContext): The migration context for tracking resource mappings.
        target_team_name (Optional[str]): Optional team name to filter migration to specific team only.

    Methods:
        _migrate_users(resources): Migrates users from OpsGenie to SquadcastUser resources.
        _migrate_teams(resources): Migrates teams from OpsGenie to SquadcastTeam resources and associates team members.
        _migrate_escalation_policies(resources): Migrates escalation policies from OpsGenie to SquadcastEscalationPolicy resources.
        transform(): Orchestrates the migration process and returns a list of TerraformResource objects.
    """

    client: OpsgenieAPIClient
    context: MigrationContext = field(default_factory=MigrationContext)
    target_team_name: Optional[str] = None

    def _migrate_users(self, resources: List[TerraformResource]) -> None:
        """Migrate users from OpsGenie to Terraform configurations."""
        logger.info("Starting OpsGenie user migration to Terraform")

        # Get target teams to determine which users to migrate
        target_teams = self._get_target_teams()
        if self.target_team_name and not target_teams:
            logger.error("Cannot proceed with user migration - target team not found")
            return
        
        # If filtering by team, only migrate users who are members of target teams
        if self.target_team_name:
            team_member_ids = self._get_team_member_ids(target_teams)
            logger.info(f"Found {len(team_member_ids)} unique users in target team(s)")
            
            if not team_member_ids:
                logger.warning("No users found in target team(s)")
                return
        
        opsgenie_users = self.client.users.list_users()
        logger.info(f"Found {len(opsgenie_users)} total users in OpsGenie")

        # Filter users if team filtering is enabled
        if self.target_team_name:
            opsgenie_users = [user for user in opsgenie_users if user.id in team_member_ids]
            logger.info(f"Filtered to {len(opsgenie_users)} users from target team(s)")

        for user in tqdm(opsgenie_users, desc="Migrating users", unit="user"):
            try:
                name_parts = user.full_name.split(" ", 1)
                squadcast_user = SquadcastUser(
                    first_name=name_parts[0] if name_parts else "",
                    last_name=name_parts[1] if len(name_parts) > 1 else "",
                    email=user.username,
                    role="user",
                )
                resources.append(squadcast_user)
                self.context.add_user(user.id, squadcast_user)
                logger.info(f"Successfully migrated user: {user.username}")

            except Exception as e:
                logger.error(f"Failed to migrate user {user.username}: {str(e)}")

    def _migrate_teams(self, resources: List[TerraformResource]) -> None:
        """Migrate teams from OpsGenie to Terraform configurations."""
        logger.info("Starting OpsGenie team migration to Terraform")

        opsgenie_teams = self._get_target_teams()
        if self.target_team_name and not opsgenie_teams:
            logger.error("Cannot proceed with team migration - target team not found")
            return
            
        logger.info(f"Found {len(opsgenie_teams)} team(s) to migrate")

        for og_team in tqdm(opsgenie_teams, desc="Migrating teams", unit="team"):
            try:
                team = self.client.teams.get_team(og_team.id)
                description = team.description or f"Team {team.name}"
                squadcast_team = SquadcastTeam(name=team.name, description=description)
                resources.append(squadcast_team)
                self.context.add_team(team.id, squadcast_team)
                team_member_ids = []

                # Add team members
                for member in team.members:
                    if not self.context.has_user(member.id):
                        logger.warning(
                            f"User {member.username} not found in migration map, skipping"
                        )
                        continue

                    user = self.context.get_user(member.id)
                    resources.append(
                        SquadcastTeamMember(
                            team_id=squadcast_team.terraform_id_reference,
                            user_id=user.terraform_id_reference,
                        )
                    )
                    team_member_ids.append(user.terraform_id_reference)
                # Create a Squadcast squad for the team
                if team_member_ids:
                    squad = self._create_squad_for_team(team.id, team_member_ids)
                    resources.append(squad)
                    self.context.add_squad(team.id, squad)
                else:
                    logger.warning(f"No members found for team {team.name}, skipping squad creation")

                logger.info(f"Successfully migrated team: {team.name}")
                
            except Exception as e:
                logger.error(f"Failed to migrate team {team.name}: {str(e)}")
    
    def _create_squad_for_team(self, team_id: str, team_member_ids: list[str]) -> SquadcastSquad:
        """Create a Squadcast squad for the given team."""
        logger.debug(f"Creating squad for team ID {team_id} with members {team_member_ids}")
        team = self.context.get_team(team_id)
        squad_name = f"{team.name} Squad"
        squad_members: List[SquadMember] = [
            SquadMember(user_id=user_id) for user_id in team_member_ids
        ]
        squad = SquadcastSquad(name=squad_name, team_id=team.terraform_id_reference, members=squad_members)
        return squad
                
    def _migrate_escalation_policies(self, resources: List[TerraformResource]) -> None:
        """Migrate escalation policies from OpsGenie to Terraform configurations."""
        logger.info("Starting OpsGenie escalation policy migration to Terraform")
        
        opsgenie_policies = self.client.escalation_policies.list_policies()
        logger.info(f"Found {len(opsgenie_policies)} escalation policies in OpsGenie")
        
        # Filter policies by target team if specified
        if self.target_team_name:
            target_team_ids = {team.id for team in self._get_target_teams()}
            opsgenie_policies = [
                policy for policy in opsgenie_policies 
                if policy.owner_team and policy.owner_team.id in target_team_ids
            ]
            logger.info(f"Filtered to {len(opsgenie_policies)} escalation policies for target team(s)")
        
        # Map policies to Squadcast format
        for policy in tqdm(opsgenie_policies, desc="Migrating escalation policies", unit="policy"):
            logger.info(f"Processing policy: {policy.name} (ID: {policy.id})")
            logger.debug(f"Policy details: {vars(policy)}")
            try:
                # Skip if team is missing
                if not policy.owner_team or not policy.owner_team.id:
                    logger.warning(f"Escalation policy {policy.name} has no owner team, skipping")
                    continue
                
                if not policy.rules or len(policy.rules) == 0:
                    logger.warning(f"No rules found for policy {policy.name}, skipping")
                    continue
                    
                # Skip if we haven't migrated the team
                team_id = policy.owner_team.id
                if not self.context.has_team(team_id):
                    logger.warning(
                        f"Team {policy.owner_team.name} not found in migration map, skipping escalation policy {policy.name}"
                    )
                    continue
                
                # Get the Squadcast team
                squadcast_team = self.context.get_team(team_id)
                
                squadcast_rules: List[Rule] = []
                added_schedule_targets: Dict[str, int] = {}
                
                logger.info(f"Processing {len(policy.rules)} rules for policy {policy.name}")
                
                for rule in policy.rules:
                    logger.debug(f"Rule: {vars(rule)}")

                    # Extract delay in minutes
                    delay_minutes = 0
                    if isinstance(rule.delay, dict):
                        time_amount = rule.delay.get("timeAmount", 0)
                        time_unit = rule.delay.get("timeUnit", "minutes").lower()

                        if time_unit == "minutes":
                            delay_minutes = time_amount
                        elif time_unit == "hours":
                            delay_minutes = time_amount * 60
                        elif time_unit == "seconds":
                            delay_minutes = time_amount / 60
                        else:
                            logger.warning(f"Unknown time unit: {time_unit}, defaulting to minutes")
                            delay_minutes = time_amount
                    elif isinstance(rule.delay, (int, float)):
                        delay_minutes = rule.delay

                    recipient_type = getattr(rule, 'recipient_type', None) or rule.notify_type
                    targets = self._map_recipient_to_targets(rule.recipient, recipient_type)

                    if not targets:
                        logger.warning(f"Could not map recipient for rule in policy {policy.name}, skipping rule")
                        continue

                    for target in targets:
                        is_schedule = target.type == "schedulev2"
                        schedule_id = target.id

                        round_robin = None
                        if rule.notify_type == "next":
                            round_robin = RoundRobin(enabled=True, escalate_within_round_robin=True)
                        else:
                            round_robin = RoundRobin(enabled=False, escalate_within_round_robin=False)

                        if is_schedule and schedule_id in added_schedule_targets:
                            # Schedule already added, set repeat on the original rule
                            existing_rule = squadcast_rules[added_schedule_targets[schedule_id]]
                            if existing_rule.repeat is None:
                                existing_rule.repeat = Repeat(
                                    times=1,
                                    delay_minutes=delay_minutes
                                )
                            else:
                                existing_rule.repeat.times += 1
                        else:
                            # New rule
                            new_rule = Rule(
                                delay_minutes=delay_minutes,
                                targets=[target],
                                notification_channels=["Email", "SMS", "Phone", "Push"],
                                round_robin=round_robin
                            )

                            squadcast_rules.append(new_rule)

                            if is_schedule:
                                added_schedule_targets[schedule_id] = len(squadcast_rules) - 1
                    
                logger.info(f"Mapped {len(squadcast_rules)} rules for policy {policy.name}")
                
                repeat = None
                if policy.repeat:
                    times = policy.repeat.count
                    delay = policy.repeat.waitInterval
                    if times > 0 and delay > 0:
                        repeat = Repeat(times=times, delay_minutes=delay)
                
                # Find a user to be entity owner (TODO: What can be done better here?)
                entity_owner = None
                if self.context.users:
                    first_user_id = next(iter(self.context.users.values())).terraform_id_reference
                    entity_owner = EntityOwner(id=first_user_id, type="user")
                else:
                    logger.warning(f"No users available for entity_owner in policy {policy.name}")
                    continue
                
                logger.info(f"Creating Squadcast policy with {len(squadcast_rules)} rules")
                for i, rule in enumerate(squadcast_rules):
                    logger.info(f"  Rule {i+1}: delay={rule.delay_minutes}m, targets={[t.type for t in rule.targets]}")
                
                squadcast_policy = SquadcastEscalationPolicy(
                    name=policy.name,
                    team_id=squadcast_team.terraform_id_reference,
                    description=policy.description if policy.description else f"Escalation policy for {squadcast_team.name}",
                    rules=squadcast_rules,
                    repeat=repeat,
                    entity_owner=entity_owner,
                )
                
                resources.append(squadcast_policy)
                self.context.add_escalation_policy(policy.id, squadcast_policy)
                logger.info(f"Successfully migrated escalation policy: {policy.name}")
                
            except Exception as e:
                logger.error(f"Failed to migrate escalation policy {policy.name}: {str(e)}")
    
    def _map_recipient_to_targets(self, recipient_id: str, notify_type: str) -> List[Target]:
        """Map an OpsGenie recipient to Squadcast targets in Escalation Policies."""
        targets: List[Target] = []
        
        logger.debug(f"Mapping recipient: id={recipient_id}, type={notify_type}")
        
        try:
            # Default to using the provided notify_type, but normalize to lowercase for comparison
            recipient_type = notify_type.lower() if notify_type else "unknown"
            
            if recipient_type == "user":
                if self.context.has_user(recipient_id):
                    user = self.context.get_user(recipient_id)
                    targets.append(Target(id=user.terraform_id_reference, type="user"))
                    logger.debug(f"Mapped user {recipient_id} to Squadcast user")
                else:
                    logger.warning(f"User {recipient_id} not found in migration context")
            elif recipient_type == "team":
                if self.context.has_squad(recipient_id):
                    squad = self.context.get_squad(recipient_id)
                    targets.append(Target(id=squad.terraform_id_reference, type="squad"))
                    logger.debug(f"Mapped squad {recipient_id} to Squadcast squad")
                else:
                    logger.warning(f"Squad {recipient_id} not found in migration context")

            elif recipient_type == "schedule":
                if self.context.has_schedule(recipient_id):
                    schedule = self.context.get_schedule(recipient_id)
                    targets.append(Target(id=schedule.terraform_id_reference, type="schedulev2"))
                    logger.debug(f"Mapped schedule {recipient_id} to Squadcast schedule")
                else:
                    logger.warning(f"Schedule {recipient_id} not found in migration context")
                
            else:
                logger.warning(f"Unknown recipient type: {recipient_type}")
                
        except Exception as e:
            logger.error(f"Error mapping recipient {recipient_id} of type {notify_type}: {str(e)}")
            
        if not targets:
            logger.warning(f"Failed to map recipient {recipient_id} of type {notify_type} to any targets")
            
        return targets
    
    def _migrate_schedules(self, resources: List[TerraformResource]) -> None:
        """Migrate schedules from OpsGenie to Terraform configurations."""
        logger.info("Starting OpsGenie schedule migration to Terraform")
        
        opsgenie_schedules = self.client.schedules.list_schedules()
        logger.info(f"Found {len(opsgenie_schedules)} schedules in OpsGenie")
        
        # Filter schedules by target team if specified
        if self.target_team_name:
            target_team_ids = {team.id for team in self._get_target_teams()}
            opsgenie_schedules = [
                schedule for schedule in opsgenie_schedules 
                if schedule.owner_team and schedule.owner_team.id in target_team_ids
            ]
            logger.info(f"Filtered to {len(opsgenie_schedules)} schedules for target team(s)")
        
        for schedule in tqdm(opsgenie_schedules, desc="Migrating schedules", unit="schedule"):
            try:
                logger.info(f"Processing schedule: {schedule.name} (ID: {schedule.id})")
                
                # Skip if team is missing or not migrated
                if not schedule.owner_team or not schedule.owner_team.id:
                    logger.warning(f"Schedule {schedule.name} has no owner team, skipping")
                    continue
                
                team_id = schedule.owner_team.id
                if not self.context.has_team(team_id):
                    logger.warning(
                        f"Team {schedule.owner_team.name} not found in migration map, skipping schedule {schedule.name}"
                    )
                    continue
                
                # Get the Squadcast team
                squadcast_team = self.context.get_team(team_id)
                
                # Find a user to be entity owner (using the same approach as in _migrate_escalation_policies)
                entity_owner = None
                if self.context.users:
                    first_user_id = next(iter(self.context.users.values())).terraform_id_reference
                    entity_owner = EntityOwner(id=first_user_id, type="user")
                else:
                    logger.error(f"No users available to set as entity owner for schedule {schedule.name}")
                    continue
                
                # Create the Squadcast schedule
                squadcast_schedule = SquadcastSchedule(
                    name=schedule.name,
                    team_id=squadcast_team.terraform_id_reference,
                    description=schedule.description or f"Schedule {schedule.name}",
                    timezone=schedule.timezone,
                    entity_owner=entity_owner,
                )
                
                resources.append(squadcast_schedule)
                self.context.add_schedule(schedule.id, squadcast_schedule)
                logger.info(f"Successfully migrated schedule: {schedule.name}")
                
                # Process rotations for this schedule
                for rotation in schedule.rotations:
                    try:
                        self._process_rotation(resources, rotation, squadcast_schedule)
                    except Exception as e:
                        logger.error(f"Failed to migrate rotation {rotation.name} in schedule {schedule.name}: {str(e)}", traceback.format_exc())
                
            except Exception as e:
                logger.error(f"Failed to migrate schedule {schedule.name}: {str(e)}", traceback.format_exc())
    
    def _process_rotation(self, resources: List[TerraformResource], rotation: OpsGenieRotation, squadcast_schedule: SquadcastSchedule) -> None:
        """Process a single rotation from OpsGenie and add it to the resources list."""
        logger.info(f"Processing rotation: {rotation.name} (ID: {rotation.id})")
        
        # Map rotation type to period
        period_map = {
            "hourly": "daily",
            "daily": "daily",
            "weekly": "weekly",
            "custom": "custom"
        }
        
        # Default to custom if type is missing or not recognized
        rotation_type = rotation.type.lower() if hasattr(rotation, 'type') and rotation.type else "custom"
        period = period_map.get(rotation_type, "custom")
        
        # Convert start and end dates to ISO format
        start_date = rotation.start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date = rotation.end_date.strftime("%Y-%m-%dT%H:%M:%SZ") if rotation.end_date else None
        
        # Create participant groups with participants
        participant_groups: List[ParticipantGroup] = []
        for participant_data in rotation.participants:
            participants: List[Participant] = []
            
            # Get the participant type and id
            participant_type = participant_data.type
            participant_id = participant_data.id
            
            # Map participant to Squadcast entity
            if participant_type == "user" and self.context.has_user(participant_id):
                user = self.context.get_user(participant_id)
                participants.append(
                    Participant(
                        id=user.terraform_id_reference,
                        type="user"
                    )
                )
            elif participant_type == "team" and self.context.has_team(participant_id):
                team = self.context.get_team(participant_id)
                participants.append(
                    Participant(
                        id=team.terraform_id_reference,
                        type="squad"
                    )
                )
            else:
                logger.warning(f"Participant {participant_id} of type {participant_type} not found in migration context, skipping")
                continue
            
            if participants:
                participant_groups.append(ParticipantGroup(participants=participants))
        
        if not participant_groups:
            logger.warning(f"No valid participants found for rotation {rotation.name}, skipping")
            return
            
        # Handle shift timeslots for custom rotations
        shift_timeslots = None
        custom_period_frequency = None
        custom_period_unit = None
        
        if rotation.time_restriction:
            days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            restriction_type = rotation.time_restriction.type
            restrictions = rotation.time_restriction.restrictions
            restriction = rotation.time_restriction.restriction

            # For weekday-and-time-of-day restrictions, we need to handle each day separately
            if restriction_type == "weekday-and-time-of-day" and restrictions:
                custom_period_unit = "day" if period == "daily" else "week"
                custom_period_frequency = 1
                period = "custom"  # Force custom period for time-restricted rotations

                shift_timeslots: List[ShiftTimeslot] = []
                for restriction in restrictions:
                    start_day = restriction.startDay
                    end_day = restriction.endDay
                    
                    if not start_day or not end_day or start_day not in days_of_week or end_day not in days_of_week:
                        logger.warning(f"Invalid day in restriction: {restriction}")
                        continue
                    
                    start_day_index = days_of_week.index(start_day)
                    end_day_index = days_of_week.index(end_day)
                    
                    start_hour = restriction.startHour
                    start_min = restriction.startMin
                    end_hour = restriction.endHour
                    end_min = restriction.endMin
                    
                    # Check if the restriction spans across days
                    if start_day == end_day:
                        duration = (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
                        shift_timeslots.append(
                            ShiftTimeslot(
                                start_hour=start_hour,
                                start_minute=start_min,
                                duration=duration,
                                day_of_week=start_day
                            )
                        )
                    else:
                        # Multi-day restriction
                        days_between = 0
                        if end_day_index > start_day_index:
                            days_between = end_day_index - start_day_index
                        else:
                            # Handle wrap around (e.g., Sunday to Monday)
                            days_between = 7 - start_day_index + end_day_index
                        
                        # Calculate total duration in minutes
                        first_day_mins = (24 * 60) - (start_hour * 60 + start_min)
                        last_day_mins = end_hour * 60 + end_min
                        
                        # Add the first day's shift
                        shift_timeslots.append(
                            ShiftTimeslot(
                                start_hour=start_hour,
                                start_minute=start_min,
                                duration=min(1440, first_day_mins),  # Cap at 24 hours
                                day_of_week=start_day
                            )
                        )
                        
                        # If we have days in between, add full day shifts
                        if days_between > 1:
                            current_day_index = (start_day_index + 1) % 7
                            for _ in range(days_between - 1):
                                shift_timeslots.append(
                                    ShiftTimeslot(
                                        start_hour=0,
                                        start_minute=0,
                                        duration=24 * 60,  # 24 hours
                                        day_of_week=days_of_week[current_day_index]
                                    )
                                )
                                current_day_index = (current_day_index + 1) % 7
                        
                        if last_day_mins > 0:
                            shift_timeslots.append(
                                ShiftTimeslot(
                                    start_hour=0,
                                    start_minute=0,
                                    duration=last_day_mins,
                                    day_of_week=end_day
                                )
                            )
                        
            
            elif restriction_type == "time-of-day":
                start_hour = restriction.startHour
                start_min = restriction.startMin
                end_hour = restriction.endHour
                end_min = restriction.endMin
                
                start_mins = start_hour * 60 + start_min
                end_mins = end_hour * 60 + end_min
                if end_mins <= start_mins:
                    end_mins += 24 * 60
                duration = end_mins - start_mins
                
                shift_timeslots = [ShiftTimeslot(
                            start_hour=start_hour,
                            start_minute=start_min,
                            duration=duration,
                            day_of_week=None
                        )]
                    
        else:
            # Default timeslot for the whole day
            shift_timeslots = [
                ShiftTimeslot(
                    start_hour=0,
                    start_minute=0,
                    duration=24 * 60
                )
            ]
        squadcast_rotation = ScheduleRotation(
            schedule_id=squadcast_schedule.terraform_id_reference,
            name=rotation.name,
            start_date=start_date,
            period=period,
            change_participants_frequency=1,  # Default value
            change_participants_unit="rotation",  # Default value
            participant_groups=participant_groups,
            shift_timeslots=shift_timeslots,
            custom_period_frequency=custom_period_frequency,
            custom_period_unit=custom_period_unit,
            end_date=end_date
        )
        
        resources.append(squadcast_rotation)
        self.context.add_rotation(rotation.id, squadcast_rotation)
        logger.info(f"Successfully migrated rotation: {rotation.name}")
    
    def _get_target_teams(self):
        """Get the list of teams to migrate based on target_team_name filter."""
        all_teams = self.client.teams.list_teams()
        
        if self.target_team_name:
            logger.info(f"Filtering migration to team: {self.target_team_name}")
            target_teams = [team for team in all_teams if team.name.lower() == self.target_team_name.lower()]
            
            if not target_teams:
                logger.error(f"Target team '{self.target_team_name}' not found in OpsGenie")
                logger.info(f"Available teams: {[team.name for team in all_teams]}")
                return []
            
            logger.info(f"Found target team: {target_teams[0].name} (ID: {target_teams[0].id})")
            return target_teams
        else:
            logger.info("No team filter specified, migrating all teams")
            return all_teams
    
    def _get_team_member_ids(self, target_teams):
        """Get all user IDs that are members of the target teams."""
        team_member_ids = set()
        
        for team_summary in target_teams:
            try:
                team_detail = self.client.teams.get_team(team_summary.id)
                for member in team_detail.members:
                    team_member_ids.add(member.id)
            except Exception as e:
                logger.error(f"Failed to get team details for {team_summary.name}: {str(e)}")
        
        return team_member_ids

    def transform(self) -> List[TerraformResource]:
        """Transform OpsGenie resources to Terraform configurations and return as a list."""
        if self.target_team_name:
            logger.info(f"🚀 Starting filtered migration from OpsGenie to Terraform (Team: {self.target_team_name})")
        else:
            logger.info("🚀 Starting migration from OpsGenie to Terraform (All teams)")

        resources: List[TerraformResource] = []

        # First migrate users so we have them available for team membership
        logger.info("Migrating users...")
        self._migrate_users(resources)

        # Then migrate teams and their members
        logger.info("Migrating teams...")
        self._migrate_teams(resources)
        
        # Migrate schedules
        logger.info("Migrating schedules...")
        self._migrate_schedules(resources)
        
        # Migrate escalation policies
        logger.info("Migrating escalation policies...")
        self._migrate_escalation_policies(resources)
        
        logger.info("Migration complete! ✅")

        return resources
