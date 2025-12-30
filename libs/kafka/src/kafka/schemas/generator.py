"""Generator to convert Pydantic models to Avro schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union, get_args, get_origin

from pydantic import BaseModel


def python_type_to_avro_type(field_type: Any, field_default: Any = None) -> Any:
    """Convert Python/Pydantic type to Avro type.

    Args:
        field_type: Python type annotation
        field_default: Default value for the field

    Returns:
        Avro type definition (string or dict)
    """
    # Handle Optional types
    origin = get_origin(field_type)
    if origin is Optional or (origin is type(None)):
        args = get_args(field_type)
        if args:
            inner_type = args[0] if args[0] is not type(None) else args[1]
            return ["null", python_type_to_avro_type(inner_type)]
        return "null"

    # Handle Union types (excluding Optional which is handled above)
    if origin is Union:
        args = get_args(field_type)
        return [python_type_to_avro_type(arg) for arg in args if arg is not type(None)]

    # Basic types
    if field_type is str:
        return "string"
    elif field_type is int:
        return "int"
    elif field_type is float:
        return "double"
    elif field_type is bool:
        return "boolean"
    elif field_type is bytes:
        return "bytes"

    # datetime -> long with logicalType
    elif field_type is datetime:
        return {"type": "long", "logicalType": "timestamp-millis"}

    # Enum -> string with enum constraint
    elif isinstance(field_type, type) and issubclass(field_type, Enum):
        return {
            "type": "enum",
            "name": field_type.__name__,
            "symbols": [e.value for e in field_type],
        }

    # Dict -> map
    elif origin is dict or field_type is dict:
        args = get_args(field_type)
        value_type = args[1] if len(args) > 1 else "string"
        return {"type": "map", "values": python_type_to_avro_type(value_type)}

    # List -> array
    elif origin is list or field_type is list:
        args = get_args(field_type)
        item_type = args[0] if args else "string"
        return {"type": "array", "items": python_type_to_avro_type(item_type)}

    # Nested BaseModel -> record
    elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
        return generate_avro_schema_from_pydantic(field_type)

    # Default to string for unknown types
    return "string"


def generate_avro_schema_from_pydantic(
    model: type[BaseModel],
    namespace: str = "com.nextwatch.events",
    version: str = "v1",
) -> dict[str, Any]:
    """Generate Avro schema from Pydantic model.

    Args:
        model: Pydantic model class
        namespace: Avro namespace
        version: Schema version

    Returns:
        Avro schema as dictionary
    """
    fields = []

    for field_name, field_info in model.model_fields.items():
        field_type = field_info.annotation
        default = field_info.default

        avro_field: dict[str, Any] = {
            "name": field_name,
            "type": python_type_to_avro_type(field_type, default),
        }

        # Add doc if available
        if field_info.description:
            avro_field["doc"] = field_info.description

        # Add default value if present and not a factory
        if default is not None and not callable(default):
            if isinstance(default, Enum):
                avro_field["default"] = default.value
            elif not isinstance(default, type):
                avro_field["default"] = default

        fields.append(avro_field)

    schema = {
        "type": "record",
        "name": f"{model.__name__}.{version}",
        "namespace": namespace,
        "fields": fields,
    }

    # Add doc if available
    if model.__doc__:
        schema["doc"] = model.__doc__.strip()

    return schema
