# RFC 001: Terraform Provider Schema to Pydantic Models

## Overview

This RFC proposes a solution for creating type-safe Pydantic models that represent Squadcast Terraform provider resources. The models will enable validation, serialization to HCL format, and organized file generation for Terraform configurations.

## Goals

1. Create accurate Pydantic model representations of Terraform resource schemas
2. Maintain type safety and validation
3. Support nested relationships between resources
4. Enable serialization to valid HCL format
5. Implement organized file structure generation

## Detailed Design

### 1. Schema Parsing and Model Generation

The system will parse the Terraform provider schema and generate corresponding Pydantic models:

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class TerraformResource(BaseModel):
    """Base class for all Terraform resources with common metadata"""
    terraform_resource_type: str
    terraform_name: str
    
    class Config:
        extra = "forbid"  # Prevent additional attributes

class SquadcastResource(TerraformResource):
    """Base class for Squadcast-specific resources"""
    pass
```

### 2. Nested Relationships

The system handles nested relationships by using Pydantic model composition and Terraform resource references.

1. **Model Composition**: Resources with nested structures use Pydantic model composition:

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ServiceTag(BaseModel):
    key: str
    value: str

class ServiceMaintainer(BaseModel):
    id: str
    type: Literal["user", "squad"]
```

2. **Resource References**: Cross-resource references use Terraform interpolation syntax. The `TerraformResource` class provides a `terraform_id_reference` property for generating these references. In the `SquadcastService` model, `team_id` and `escalation_policy_id` are used to reference other resources:

```python
class SquadcastService(SquadcastResource):
    name: str
    team_id: str = Field(..., description="ID of the team")
    escalation_policy_id: str = Field(..., description="ID of the escalation policy")
    maintainer: ServiceMaintainer
    tags: Optional[List[ServiceTag]]
```


1. **Sets**: Python sets are automatically converted to sorted lists during HCL serialization for consistent output:

```python
class SquadcastUser(SquadcastResource):
    abilities: Optional[Set[UserAbility]] = Field(
        default=None,
        description="Set of user abilities/permissions"
    )

user = SquadcastUser(
    abilities=["manage-users", "manage-teams"]
)
```

Generated HCL:

```hcl
resource "squadcast_user" "example" {
  abilities = ["manage-teams", "manage-users"] # Note: Sorted for consistency
}
```


The following example demonstrates how complex nested structures and cross-resource references are addressed:

```python
team = SquadcastTeam(
    terraform_name="engineering",
    name="Engineering Team",
    description="Core engineering team"
)

escalation_policy = SquadcastEscalationPolicy(
    terraform_name="default_escalation_policy",
    name="Default Escalation Policy",
    team_id=team.terraform_id_reference  # Reference the team
)

service = SquadcastService(
    terraform_name="api_service",
    name="API Service",
    team_id=team.terraform_id_reference,  # Reference to team
    escalation_policy_id=escalation_policy.terraform_id_reference,  # Reference to escalation policy
    email_prefix="api-alerts",
    maintainer=ServiceMaintainer(
        id="${squadcast_user.lead_engineer.id}",
        type="user"
    ),
    tags=[
        ServiceTag(key="environment", value="production"),
        ServiceTag(key="team", value="engineering")
    ],
    alert_sources=["datadog", "prometheus"]
)

# Generate HCL
hcl = service.to_hcl()
print(hcl)
```

Generated HCL:

```hcl
resource "squadcast_service" "api_service" {
  name = "API Service"
  team_id = "${squadcast_team.engineering.id}"
  escalation_policy_id = "${squadcast_escalation_policy.default_escalation_policy.id}"
  email_prefix = "api-alerts"

  maintainer {
    id = "${squadcast_user.lead_engineer.id}"
    type = "user"
  }

  tags {
    key = "environment"
    value = "production"
  }

  tags {
    key = "team"
    value = "engineering"
  }

  alert_sources = ["datadog", "prometheus"]
}
```

### 3. Resource Models

Example resource model structure:

```python
class SquadcastTeam(SquadcastResource):
    name: str = Field(..., description="Name of the team")
    description: Optional[str] = None
    members: List[str] = Field(default_factory=list)
    
    terraform_resource_type = "squadcast_team"
```

### 4. File Organization

Generated Terraform files will follow this structure:

```
terraform/
├── teams/
│   ├── main.tf
│   └── variables.tf
├── escalation_policies/
│   ├── main.tf
│   └── variables.tf
├── services/
│   ├── main.tf
│   └── variables.tf
└── providers.tf
```

### 5. Implementation Phases

1. Schema Analysis
   - Parse provider schema
   - Identify resource types and relationships
   - Map data types to Pydantic field types

2. Model Generation
   - Create base model classes
   - Implement nested relationships
   - Add validation rules

3. HCL Serialization
   - Implement serialization logic
   - Handle special HCL syntax requirements
   - Support nested block structures

4. File Generation
   - Create directory structure
   - Generate modular Terraform files
   - Implement resource organization

### 6. Resource Dependencies and References

The system handles resource dependencies and references using explicit references, ensuring proper linking and dependency management.

1. **Explicit References**:
   - Use Terraform interpolation syntax (`${resource_type.name.attribute}`)
   - References are type-checked at the Pydantic model level
   - HCL serialization preserves reference relationships

The system ensures that these dependencies are correctly formatted in the HCL output.

The configuration manager tracks implicit dependencies and generates resources in the correct order. Circular dependencies are handled through Terraform references, ensuring that resources are created in the correct order.

### 7. Example Usage

The following example demonstrates how nested resolution works with the generated Terraform configuration:

```python
team = SquadcastTeam(
    terraform_name="engineering",
    name="Engineering Team",
    description="Core engineering team"
)

escalation_policy = SquadcastEscalationPolicy(
    terraform_name="default_escalation_policy",
    name="Default Escalation Policy",
    team_id=team.terraform_id_reference  # Reference the team
)

service = SquadcastService(
    terraform_name="api_service",
    name="API Service",
    team_id=team.terraform_id_reference,  # Reference to team
    escalation_policy_id=escalation_policy.terraform_id_reference,  # Reference to escalation policy
    email_prefix="api-alerts",
    maintainer=ServiceMaintainer(
        id="${squadcast_user.lead_engineer.id}",
        type="user"
    ),
    tags=[
        ServiceTag(key="environment", value="production"),
        ServiceTag(key="team", value="engineering")
    ],
    alert_sources=["datadog", "prometheus"]
)

# Generate HCL
hcl = service.to_hcl()
print(hcl)
```

Generated HCL:

```hcl
resource "squadcast_service" "api_service" {
  name = "API Service"
  team_id = "${squadcast_team.engineering.id}"
  escalation_policy_id = "${squadcast_escalation_policy.default_escalation_policy.id}"
  email_prefix = "api-alerts"

  maintainer {
    id = "${squadcast_user.lead_engineer.id}"
    type = "user"
  }

  tags {
    key = "environment"
    value = "production"
  }

  tags {
    key = "team"
    value = "engineering"
  }

  alert_sources = ["datadog", "prometheus"]
}
```

In this example, the `team_id` and `escalation_policy_id` in the `SquadcastService` resource use Terraform interpolation syntax to reference the `SquadcastTeam` and `SquadcastEscalationPolicy` resources. The `_format_hcl_value` method ensures that these references are correctly formatted in the generated HCL.

## Benefits

1. Type Safety: Catch configuration errors early through Pydantic validation
2. Maintainability: Structured code organization and clear model relationships
3. Reliability: Consistent HCL generation with proper syntax
4. Extensibility: Easy to add new resource types and validation rules
5. Developer Experience: IDE autocompletion and type hints

## Implementation Timeline

1. Week 1: Schema analysis and base model implementation
2. Week 2: Resource models and validation
3. Week 3: HCL serialization
4. Week 4: File generation and testing

## Open Questions

1. How to handle provider-specific functions and interpolation?
2. What level of validation should be implemented beyond schema types?
3. How to manage state file integration if needed?

## Next Steps

1. Set up project structure
2. Implement base models and serialization
3. Create test cases
4. Document usage and examples.
