# OpsGenie Client Implementation Guide

A guide for solution engineers on how to use and extend the OpsGenie client.

## Overview

The OpsGenie client is designed to be:

- Simple to use for migrations
- Easy to extend with new resources
- Type-safe with clear interfaces

## Basic Usage

```python
from squadcastify.source.opsgenie import OpsgenieAPIClient

client = OpsgenieAPIClient(api_key="your-api-key")

# List all users
users = client.users.list_users()

# Get team details
team = client.teams.get_team("team-id")
```

## Creating a Model

Let's look at how to create a model using the User resource as an example:

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from .base import OpsGenieModel

@dataclass
class OpsGenieUser(OpsGenieModel):
    """Represents a user in OpsGenie."""
    
    # Required fields
    username: str
    full_name: str
    
    # Optional fields with defaults
    role: Optional[str] = None
    time_zone: Optional[str] = None
    locale: Optional[str] = None
    user_address: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    blocked: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OpsGenieUser':
        """
        Create a user instance from API response data.
        
        This method handles:
        1. Field name conversion (e.g., fullName -> full_name)
        2. Nested data extraction (e.g., role.name -> role)
        3. Optional fields
        """
        return cls(
            id=data["id"],
            username=data["username"],
            full_name=data.get("fullName", ""),
            role=data.get("role", {}).get("name"),
            time_zone=data.get("timeZone"),
            locale=data.get("locale"),
            user_address=data.get("userAddress"),
            created_at=data.get("createdAt"),
            blocked=data.get("blocked", False)
        )
```

Key points about models:

1. Inherit from `OpsGenieModel`:
   - Provides common fields (like `id`)
   - Handles base serialization

2. Use type hints:
   - Required fields without defaults
   - Optional fields with defaults
   - Use appropriate types (str, bool, dict, etc.)

3. Implement `from_dict`:
   - Convert API response format to model
   - Handle missing or optional fields
   - Convert field names to Python style

4. Handle nested data:
   - Extract nested fields (like role.name)
   - Flatten when it makes sense
   - Keep complex structures as dicts if needed

## Adding a Resource Client

After creating a model, implement its client:

```python
from typing import List
from .base import BaseResource
from ..models.user import OpsGenieUser

class UsersClient(BaseResource[OpsGenieUser]):
    """Client for user operations."""
    
    def __init__(self, http_client):
        super().__init__(http_client, OpsGenieUser)
    
    def list_users(self) -> List[OpsGenieUser]:
        """Get all users."""
        return self._get_all("users")

    def get_user(self, user_id: str) -> OpsGenieUser:
        """Get a specific user."""
        return self._get_single(f"users/{user_id}")
```

## Adding Your Own Resource

Let's see a complete example of adding a new resource:

1. Create model file `client/models/widget.py`:

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .base import OpsGenieModel

@dataclass
class OpsGenieWidget(OpsGenieModel):
    """Represents a widget in OpsGenie."""
    
    # Required fields
    name: str
    type: str
    
    # Optional fields
    description: Optional[str] = None
    enabled: bool = True
    properties: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OpsGenieWidget':
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            description=data.get("description"),
            enabled=data.get("enabled", True),
            properties=data.get("properties", {})
        )
```

2. Create client file `client/resources/widgets.py`:

```python
from typing import List
from .base import BaseResource
from ..models.widget import OpsGenieWidget

class WidgetsClient(BaseResource[OpsGenieWidget]):
    """Client for widget operations."""
    
    def __init__(self, http_client):
        super().__init__(http_client, OpsGenieWidget)
    
    def list_widgets(self) -> List[OpsGenieWidget]:
        """Get all widgets."""
        return self._get_all("widgets")
        
    def get_widget(self, widget_id: str) -> OpsGenieWidget:
        """Get a specific widget."""
        return self._get_single(f"widgets/{widget_id}")
```

3. Add to `OpsgenieAPIClient` in `client/api.py`:

```python
from .resources.widgets import WidgetsClient

class OpsgenieAPIClient:
    def __init__(self, api_key: str):
        self.http = HTTPClient(api_key)
        self.widgets = WidgetsClient(self.http)
```

## Key Components

### Base Model (`models/base.py`)

- All models inherit from `OpsGenieModel`
- Provides common functionality like ID field
- Handle data conversion from API responses

### Base Resource (`resources/base.py`)

- Generic base class for all resource clients
- Handles pagination and response parsing
- Common CRUD operations

### HTTP Client (`http.py`)

- Makes requests to OpsGenie API
- Handles authentication
- Error handling and retries

## Error Handling

The client has built-in error types:

```python
try:
    team = client.teams.get_team("invalid-id")
except OpsGenieNotFoundError:
    print("Team not found")
except OpsGenieAuthenticationError:
    print("Invalid API key")
```

## Best Practices

1. Use dataclasses for models:
   - Clear field definitions
   - Type hints for all fields
   - Default values for optional fields

2. Keep resource clients focused:
   - One client per resource type
   - Clear method names
   - Document parameters and return types

3. Handle pagination:
   - Use `_get_all()` from base resource
   - Let client handle pagination automatically

4. Add error handling:
   - Use appropriate error types
   - Document possible errors
   - Include error details in exceptions

5. Add docstrings:
   - Document all public methods
   - Include parameter descriptions
   - Show usage examples for complex operations
