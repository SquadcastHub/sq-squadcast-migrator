from typing import Optional, Dict, Any, Type
from pydantic import BaseModel, Field, ConfigDict

from .utils import generate_terraform_name


class TerraformResource(BaseModel):
    """Base class for all Terraform resources with common metadata"""
    model_config = ConfigDict(extra="forbid")

    terraform_name: str = Field(
        ...,
        description="The name/identifier of the resource in Terraform configuration"
    )

    def to_hcl(self) -> str:
        """Convert the resource to HCL format"""
        # Convert model to dict, excluding None values
        data = self.model_dump(exclude_none=True, exclude={'terraform_name'})
        
        # Start with resource definition
        hcl = [f'resource "{self.terraform_resource_type}" "{self.terraform_name}" {{']
        
        # Add fields
        for key, value in data.items():
            formatted_value = self._format_hcl_value(value)
            hcl.append(f'  {key} = {formatted_value}')
        
        hcl.append('}')
        return '\n'.join(hcl)

    # HCL formatting constants
    _HCL_INDENT = "  "
    _HCL_NEWLINE = "\n"
    
    def _format_hcl_value(self, value: Any) -> str:
        """Format a value according to HCL syntax rules.
        
        Args:
            value: The value to format. Can be one of:
                - TerraformResource: Formatted as a resource reference
                - str: Wrapped in quotes
                - bool: Converted to lowercase 'true' or 'false'
                - list/tuple/set: Formatted as HCL list
                - dict: Formatted as HCL map
                - BaseModel: Formatted as HCL block
                - int/float: Converted to string
                - None: Raises ValueError
        
        Returns:
            str: The HCL-formatted value
            
        Raises:
            ValueError: If the value is None or has an unsupported type
            TypeError: If a dict key is not a string
        """
        if value is None:
            raise ValueError("HCL cannot represent None/null values")

        """Format a value according to HCL syntax rules.
        
        Args:
            value: The value to format. Can be one of:
                - TerraformResource: Formatted as a resource reference
                - str: Wrapped in quotes
                - bool: Converted to lowercase 'true' or 'false'
                - list/tuple: Formatted as HCL list
                - dict: Formatted as HCL map
                - BaseModel: Formatted as HCL block
                - int/float: Converted to string
                - None: Raises ValueError
        
        Returns:
            str: The HCL-formatted value
            
        Raises:
            ValueError: If the value is None or has an unsupported type
            TypeError: If a dict key is not a string
        """
        if value is None:
            raise ValueError("HCL cannot represent None/null values")

        # Optimize type checking order based on common cases
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, TerraformResource):
            return value.terraform_id_reference
            
        # Handle container types with validation
        if isinstance(value, (list, tuple, set)):
            try:
                # Convert set to sorted list for consistent output
                if isinstance(value, set):
                    value = sorted(value, key=str)
                items = [self._format_hcl_value(item) for item in value]
                return f'[{", ".join(items)}]'
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid sequence item in {type(value).__name__}: {str(e)}")
                
        if isinstance(value, dict):
            try:
                formatted_items = []
                for k, v in value.items():
                    if not isinstance(k, str):
                        raise TypeError(f"Dictionary keys must be strings, got {type(k)}")
                    formatted_value = self._format_hcl_value(v)
                    formatted_items.append(f'{k} = {formatted_value}')
                return f'{{{", ".join(formatted_items)}}}'
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid dictionary entry: {str(e)}")
                
        if isinstance(value, BaseModel):
            try:
                data = value.model_dump(exclude_none=True)
                items = [
                    f'{k} = {self._format_hcl_value(v)}'
                    for k, v in data.items()
                ]
                joined_items = self._HCL_NEWLINE.join(
                    f'{self._HCL_INDENT}{item}' for item in items
                )
                return f'{{\n{joined_items}\n}}'
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid model data: {str(e)}")
        
        raise ValueError(
            f"Cannot format value of type {type(value).__name__} as HCL"
        )

    @property
    def terraform_resource_type(self) -> str:
        """Return the Terraform resource type (must be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement terraform_resource_type")

    @property
    def terraform_id_reference(self) -> str:
        """Return the Terraform ID reference for this resource.
        
        This is used when this resource is referenced by another resource.
        Example: "${squadcast_team.engineering.id}"
        """
        return f"${{{self.terraform_resource_type}.{self.terraform_name}.id}}"


class ReadOnlyField:
    """Descriptor for read-only Terraform fields"""
    def __init__(self, field_type: type):
        self.field_type = field_type
        self.private_name = None

    def __set_name__(self, owner, name):
        self.private_name = f'__{name}'

    def __get__(self, instance, owner):
        if instance is None:
            return None
        return getattr(instance, self.private_name, None)

    def __set__(self, instance, value):
        if not hasattr(instance, self.private_name):
            setattr(instance, self.private_name, value)
        else:
            raise ValueError(f"Cannot modify read-only field {self.field_type}")