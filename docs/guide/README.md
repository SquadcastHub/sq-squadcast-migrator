# SolarWinds Incident Response Migrator Implementation Guides

Welcome to the SolarWinds Incident Response Migrator implementation guides. These guides provide comprehensive documentation for solution engineers implementing migrations from various alert management systems to SolarWinds Incident Response.

## Getting Started

The SolarWinds Incident Response Migrator consists of two main components:

1. Source API Clients - Handle communication with source platforms (e.g., OpsGenie)
2. Transformers - Convert source data into SolarWinds Incident Response Terraform configurations

To implement a new migration source, you'll typically:

1. Create a client to interact with the source API
2. Implement a transformer to convert source data to SolarWinds Incident Response format
3. Test the migration with sample data

## Architecture Overview

The system follows a layered architecture:

```
┌─────────────────┐
│  Source Client  │  ← Handles API communication
├─────────────────┤
│   Transformer   │  ← Converts data formats
├─────────────────┤
│ Terraform Model │  ← Defines target structure
└─────────────────┘
```

- **Source Clients** handle authentication, API requests, and data retrieval
- **Transformers** map source data to SolarWinds Incident Response's data model
- **Terraform Models** define the structure for SolarWinds Incident Response resources

## Available Guides

### [OpsGenie Client Implementation Guide](./opsgenie-client-implementation-guide.md)

This guide covers:

- Basic client usage and setup
- Creating new resource models
- Implementing resource clients
- Error handling and best practices
- Adding custom resources

### [Transformer Implementation Guide](./implementing-transformer.md)

This guide explains:

- Transformer architecture and responsibilities
- Using MigrationContext for state management
- Resource mapping patterns
- Error handling strategies
- Testing transformers

## How Components Work Together

### Client-Transformer Relationship

The client and transformer work in tandem:

1. **Client** retrieves data from the source system:
   - Handles authentication and API communication
   - Provides typed models for source data
   - Manages pagination and error handling

2. **Transformer** processes this data:
   - Uses the client to fetch resources
   - Maintains relationships between resources
    - Converts to SolarWinds Incident Response's data model

### Implementation Patterns

When implementing a new migration source:

1. Start with the client:
   - Implement basic authentication
   - Create models for core resources
   - Add resource clients for API endpoints

2. Then create the transformer:
   - Use the client to fetch data
    - Map source models to SolarWinds Incident Response models
   - Handle resource dependencies

## Best Practices

### Client Implementation

- Use type hints consistently
- Implement proper error handling
- Document API methods thoroughly
- Keep resource clients focused
- Use dataclasses for models

### Transformer Implementation

- Order resources by dependencies
- Use MigrationContext to track relationships
- Implement robust error handling
- Add detailed logging
- Test with various data scenarios

### General Guidelines

- Follow the existing patterns in the codebase
- Add comprehensive documentation
- Include usage examples
- Write tests for new functionality
- Handle edge cases gracefully

The guides provide detailed examples and implementation details for each component. Start with the client guide if you're implementing a new source API integration, or the transformer guide if you're working on data conversion logic.
