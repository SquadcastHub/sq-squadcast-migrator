# OpsGenie Client Refactoring

## Overview
The OpsGenie client has been refactored into a modular package with clear separation of concerns and improved maintainability.

## Package Structure
```
squadcastify/source/opsgenie/client/
├── __init__.py          # Package exports
├── api.py              # Main client class
├── http.py             # HTTP client
├── errors.py           # Exception classes
├── models/             # Resource models
│   ├── __init__.py
│   ├── base.py         # Base model
│   ├── user.py         # User models
│   ├── team.py         # Team models
│   ├── escalation.py   # Escalation policy models
│   └── schedule.py     # Schedule models
├── resources/          # Resource clients
│   ├── __init__.py
│   ├── base.py         # Base resource client
│   ├── users.py        # User operations
│   ├── teams.py        # Team operations
│   ├── escalation_policies.py
│   └── schedules.py
└── tests/             # Test suite
    ├── validate_api.py
    └── test_api_responses.py
```

## Key Changes
1. **Modular Design**
   - Separate modules for models and resource clients
   - Clean separation of concerns
   - Easy to extend for new resources

2. **Improved Type Safety**
   - Domain models with proper typing
   - Clear interfaces for resources
   - Type validation for API responses

3. **Better Error Handling**
   - Custom exception hierarchy
   - Detailed error information
   - HTTP status code mapping

4. **Simplified Pagination**
   - Automatic pagination handling
   - Fetches all items in collections
   - Consistent implementation across resources

5. **Test Coverage**
   - Unit tests with sample responses
   - API validation against spec
   - Live API testing support

## Usage Example
```python
from squadcastify.source.opsgenie import OpsgenieAPIClient

# Initialize client
client = OpsgenieAPIClient(api_key="your-api-key")

# Get all users
users = client.users.list_users()
for user in users:
    print(f"User: {user.username}")

# Get team details
team = client.teams.get_team("team-id")
print(f"Team: {team.name}")
for member in team.members:
    print(f"- {member.username} ({member.role})")
```

## Testing
Tests can be run using Uv:
```bash
# Install test dependencies
uv pip install -e ".[test]"

# Run tests
pytest squadcastify/source/opsgenie/client/tests/
```

## Future Improvements
1. **Additional Resources**: Add support for more OpsGenie resources as needed
2. **API Versioning**: Add version negotiation for API compatibility
3. **Rate Limiting**: Implement automatic rate limit handling

## Migration Guide
The new client is accessed through `squadcastify.source.opsgenie.OpsgenieAPIClient`. Existing code using the old client should be updated to use the new modular interface.

```python
# Old usage
from squadcastify.source.opsgenie import OpsGenieClient
client = OpsGenieClient(api_key)
users = client.get_users()

# New usage
from squadcastify.source.opsgenie import OpsgenieAPIClient
client = OpsgenieAPIClient(api_key)
users = client.users.list_users()