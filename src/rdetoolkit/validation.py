import json
import os
from pathlib import Path
from typing import Any, Optional, Union

from jsonschema import ValidationError as SchemaValidationError
from jsonschema import validate
from pydantic import ValidationError

from rdetoolkit.exceptions import InvoiceSchemaValidationError, MetadataDefValidationError
from rdetoolkit.models.invoice_schema import InvoiceSchemaJson
from rdetoolkit.models.metadata import MetadataDefItem


class MetadataDefValidator:
    def __init__(self) -> None:
        self.schema = MetadataDefItem

    def validate(self, *, path: Optional[str] = None, json_obj: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Validates the provided JSON data against the MetadataDefItem schema.

        Args:
            path (str, optional): The path to the JSON file to be validated. Defaults to None.
            json_obj (dict[str, Any], optional): The JSON object to be validated. Defaults to None.

        Returns:
            dict[str, Any]: The validated JSON data.

        Raises:
            ValueError: If neither 'path' nor 'json_obj' is provided.
            ValueError: If both 'path' and 'json_obj' are provided.
            ValueError: If an unexpected error occurs.

        """
        if path is None and json_obj is None:
            raise ValueError("At least one of 'path' or 'json_obj' must be provided")
        elif path is not None and json_obj is not None:
            raise ValueError("Both 'path' and 'json_obj' cannot be provided at the same time")

        if path is not None:
            with open(path, encoding="utf-8") as f:
                __data = json.load(f)
        elif json_obj is not None:
            __data = json_obj
        else:
            raise ValueError("Unexpected error")

        try:
            MetadataDefItem(**__data)
        except ValidationError as e:
            raise MetadataDefValidationError(f"Error in validating metadata_def.json: {e}")
        return __data


def validator(*, path: Optional[str] = None, json_obj: Optional[dict[str, Any]] = None) -> "MetadataDefItem":
    """Validator for metadata_def.json.

    Args:
        path (str, optional): File path of metadata_def.json. Defaults to None.
        json_obj (dict[str, Any], optional): Json Object of metadata_def.json. Defaults to None.

    Retrun:
        MetadataDefItem: The validated metadata_def.json object.

    Raises:
        ValueError: If neither 'path' nor 'json_obj' is provided, or if both are provided.

    Note:
        Either 'path' or 'json_obj' must be provided, but not both.
    """
    if path is None and json_obj is None:
        raise ValueError("At least one of 'path' or 'json_obj' must be provided")
    elif path is not None and json_obj is not None:
        raise ValueError("Both 'path' and 'json_obj' cannot be provided at the same time")

    if path is not None:
        with open(path, encoding="utf-8") as f:
            __data = json.load(f)
    elif json_obj is not None:
        __data = json_obj
    else:
        raise ValueError("Unexpected error")

    return MetadataDefItem(**__data)


class InvoiceValidator:
    pre_basic_info_schema = os.path.join(os.path.dirname(__file__), "static", "invoice_basic_and_sample.schema_.json")

    def __init__(self, schema_path: Union[str, Path]):
        self.schema_path = schema_path
        self.schema = self.__pre_validate()

    def __pre_validate(self) -> dict[str, Any]:
        if isinstance(self.schema_path, str):
            __path = Path(self.schema_path)
        else:
            __path = self.schema_path

        if __path.suffix != ".json":
            raise ValueError("The schema file must be a json file")

        with open(__path, encoding="utf-8") as f:
            data = json.load(f)

        if __path.name == "invoice.schema.json":
            try:
                InvoiceSchemaJson(**data)
            except Exception:
                raise ValidationError("Error in schema validation")
            return data
        else:
            return data

    def validate(self, *, path: Optional[Union[str, Path]] = None, obj: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Validate the provided JSON data against the schema.

        Args:
            path (Optional[Union[str, Path]]): The path to the JSON file to validate.
            obj (Optional[dict[str, Any]]): The JSON object to validate.

        Raises:
            ValueError: If neither 'path' nor 'obj' is provided.
            ValueError: If both 'path' and 'obj' are provided.

        Returns:
            None
        """
        if path is None and obj is None:
            raise ValueError("At least one of 'path' or 'obj' must be provided")
        elif path is not None and obj is not None:
            raise ValueError("Both 'path' and 'obj' cannot be provided at the same time")

        if path is not None:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = obj

        with open(self.pre_basic_info_schema, encoding="utf-8") as f:
            basic_info = json.load(f)
        try:
            validate(instance=data, schema=basic_info)
        except SchemaValidationError as e:
            raise InvoiceSchemaValidationError(f"Error in validating system standard item in 'invoice.schema.json': {e}")

        try:
            validate(instance=data, schema=self.schema)
        except SchemaValidationError as e:
            raise InvoiceSchemaValidationError(f"Error in validating invoice.schema.json: {e.message}")

        return data
