# Implementing a Transformer

This guide explains how to implement a new Transformer class for migrating resources from source APIs to Squadcast. We'll use the OpsGenieTransformer as a reference implementation to demonstrate key concepts and best practices.

## Transformer Overview

A Transformer is responsible for:

1. Fetching resources from the source API
2. Converting them to Squadcast's Terraform resource models
3. Maintaining state during migration using a MigrationContext
4. Handling relationships between resources

## Basic Structure

Here's the basic structure of a Transformer:

```python
@dataclass
class YourTransformer(Transformer):
    """
    YourTransformer migrates resources from SourceAPI to Terraform configurations.
    
    Document what resources this transformer handles and any special considerations.
    """
    
    client: YourAPIClient  # Client for source API
    context: MigrationContext = field(default_factory=MigrationContext)
    
    def transform(self) -> List[TerraformResource]:
        """Transform source resources to Terraform configurations."""
        logger.info("🚀 Starting migration from Source to Terraform")
        
        resources: List[TerraformResource] = []
        
        # Implement migration logic here
        # Typically ordered by dependency (e.g., users before teams)
        
        return resources
```

## Using Migration Context

The MigrationContext helps track relationships between source and target resources. This is crucial when resources have dependencies (like team members needing user references).

Example usage:

```python
@dataclass
class MigrationContext:
    """Tracks migration state between source and target resources."""
    
    users: Dict[str, SquadcastUser] = field(default_factory=dict)
    teams: Dict[str, SquadcastTeam] = field(default_factory=dict)
    
    def add_user(self, source_id: str, user: SquadcastUser) -> None:
        self.users[source_id] = user
        
    def get_user(self, source_id: str) -> SquadcastUser:
        return self.users[source_id]
```

Best practices for context:

- Create methods for each type of resource mapping
- Use typing for better code maintainability
- Keep the context focused on mapping relationships

## Resource Mapping Patterns

When mapping resources, follow these patterns:

1. Map core attributes first:

```python
squadcast_user = SquadcastUser(
    first_name=source_user.first_name,
    last_name=source_user.last_name,
    email=source_user.email,
    role="user"
)
```

2. Track the mapping in context:

```python
self.context.add_user(source_user.id, squadcast_user)
```

3. Handle relationships using context:

```python
# When creating team members, look up user references
if self.context.has_user(member.id):
    user = self.context.get_user(member.id)
    team_member = SquadcastTeamMember(
        team_id=team.terraform_id_reference,
        user_id=user.terraform_id_reference
    )
```

## Error Handling

Implement robust error handling:

1. Use try-except blocks for each resource:

```python
try:
    # Migration logic here
    logger.info(f"Successfully migrated resource: {resource.name}")
except Exception as e:
    logger.error(f"Failed to migrate resource {resource.name}: {str(e)}")
```

2. Continue on errors for individual resources:

- Log errors but continue processing
- Use warning logs for skipped resources
- Maintain detailed error messages

## Best Practices

1. **Resource Ordering**:
   - Migrate independent resources first (e.g., users)
   - Then migrate dependent resources (e.g., teams, team members)

2. **Progress Tracking**:
   - Use tqdm for progress bars
   - Log start/completion of each phase
   - Include resource counts in logs

3. **Code Organization**:
   - Split complex migrations into private methods
   - Group related resources together
   - Keep transform() method as orchestrator

4. **Documentation**:
   - Document transformer purpose and behavior
   - List all resource types handled
   - Include examples of complex mappings

## Example: Resource Migration Method

Here's a complete example of a resource migration method:

```python
def _migrate_teams(self, resources: List[TerraformResource]) -> None:
    """Migrate teams from source to Terraform configurations."""
    logger.info("Starting team migration to Terraform")
    
    source_teams = self.client.teams.list_teams()
    logger.info(f"Found {len(source_teams)} teams in source")
    
    for team in tqdm(source_teams, desc="Migrating teams", unit="team"):
        try:
            # Map core attributes
            squadcast_team = SquadcastTeam(
                name=team.name,
                description=team.description or f"Team {team.name}"
            )
            
            # Track in context and resources
            resources.append(squadcast_team)
            self.context.add_team(team.id, squadcast_team)
            
            # Handle relationships (team members)
            for member in team.members:
                if not self.context.has_user(member.id):
                    logger.warning(f"User {member.username} not found, skipping")
                    continue
                    
                user = self.context.get_user(member.id)
                resources.append(
                    SquadcastTeamMember(
                        team_id=squadcast_team.terraform_id_reference,
                        user_id=user.terraform_id_reference
                    )
                )
            
            logger.info(f"Successfully migrated team: {team.name}")
            
        except Exception as e:
            logger.error(f"Failed to migrate team {team.name}: {str(e)}")
```

## Testing Your Transformer

1. Test with small datasets first
2. Verify resource references are correct
3. Ensure all required fields are mapped
4. Check error handling with invalid data
5. Validate Terraform resource generation

Remember to handle API rate limits, pagination, and other source-specific considerations in your implementation.
