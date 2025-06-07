import re


def to_snake_case(text: str) -> str:
    """Convert any string to snake_case format.
    
    Examples:
        "My Service Name" -> "my_service_name"
        "API Service-2" -> "api_service_2"
        "TeamName" -> "team_name"
    """
    # Replace non-word characters with spaces
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    
    # Convert to lowercase and replace spaces/hyphens with underscores
    return re.sub(r'[^a-z0-9]+', '_', s2.lower()).strip('_')


def generate_terraform_name(name: str, prefix: str = '') -> str:
    """Generate a Terraform-compatible resource name from a display name.
    
    Args:
        name: The display name to convert
        prefix: Optional prefix to add to the name
    
    Returns:
        A Terraform-compatible name in snake_case format
    
    Examples:
        generate_terraform_name("My API Service") -> "my_api_service"
        generate_terraform_name("Team 1", "eng") -> "eng_team_1"
    """
    snake_case = to_snake_case(name)
    if prefix:
        prefix = to_snake_case(prefix)
        return f"{prefix}_{snake_case}"
    return snake_case