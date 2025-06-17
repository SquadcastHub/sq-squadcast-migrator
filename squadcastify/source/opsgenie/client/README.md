# OpsGenie API Client

A clean, modular client for OpsGenie API focused on migration use cases.

## Usage

```python
from squadcastify.source.opsgenie import OpsgenieAPIClient

# Initialize client
client = OpsgenieAPIClient(api_key="your-api-key")

# Get all users
users = client.users.list_users()
for user in users:
    print(f"User: {user.username}")

# Get all teams
teams = client.teams.list_teams()
for team in teams:
    print(f"Team: {team.name}")
    for member in team.members:
        print(f"- {member.username}")

# Get policies and schedules
policies = client.escalation_policies.list_policies()
schedules = client.schedules.list_schedules()
```

## Available Resources

### Users
- `client.users.list_users()`: Get all users
- `client.users.get_user(id)`: Get specific user

### Teams
- `client.teams.list_teams()`: Get all teams
- `client.teams.get_team(id)`: Get team with members

### Escalation Policies
- `client.escalation_policies.list_policies()`: Get all policies
- `client.escalation_policies.get_policy(id)`: Get specific policy

### Schedules
- `client.schedules.list_schedules()`: Get all schedules
- `client.schedules.get_schedule(id)`: Get schedule with rotations
- `client.schedules.list_timeline(id, start, end)`: Get schedule timeline

## Error Handling

```python
from squadcastify.source.opsgenie import OpsGenieError, OpsGenieNotFoundError

try:
    team = client.teams.get_team("non-existent-id")
except OpsGenieNotFoundError:
    print("Team not found")
except OpsGenieError as e:
    print(f"API error: {e}")
```

## Design Notes

1. Simple, focused implementation for migration use cases
2. Automatic pagination handling for listing resources
3. Clean separation between API resources
4. Type-safe models with clear interfaces