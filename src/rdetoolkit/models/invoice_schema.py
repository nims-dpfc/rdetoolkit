from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator


class LangLabels(BaseModel):
    """A class representing labels in different languages."""

    ja: str
    en: str


class Placeholder(BaseModel):
    """A class representing placeholders in different languages.

    This class inherits from `BaseModel`, and the `ja` and `en` attributes hold the placeholders in Japanese and English, respectively.

    `properties.custom.properties.<custom key>.options.placeholder` is an instance of this class.
    """

    ja: str
    en: str


class Options(BaseModel):
    """Represents the options for a widget in the invoice schema.

    `properties.custom.properties.<custom key>.options` is an instance of this class.

    Attributes:
        widget (Optional[Literal["textarea"]]): The type of widget. Defaults to None.
        rows (Optional[int]): The number of rows for a textarea widget. Defaults to None.
        unit (Optional[str]): The unit of measurement for the widget. Defaults to None.
        placeholder (Optional[Placeholder]): The placeholder text for the widget. Defaults to None.
    """

    widget: Optional[Literal["textarea"]] = None
    rows: Optional[int] = None
    unit: Optional[str] = None
    placeholder: Optional[Placeholder] = None

    @model_validator(mode="after")
    def __check_row_for_widget_textarea(self):
        """Validates that the 'row' field is set when the 'widget' field is set to 'textarea'.

        Args:
            v (Optional[int]): The value of the 'row' field to be validated. This value must not be None if the widget is set to 'textarea'.
            values (dict): A dictionary containing the values of other fields in the instance. Specifically, the value of the 'widget' field is retrieved from this dictionary.

        Raises:
            ValueError: If the widget is set to 'textarea' and the 'row' is not set (None or not provided).

        Returns:
            Optional[int]: The validated value of the 'row' field. Returns the input value (v) if there are no issues.
        """
        if self.rows is None and self.widget is not None:
            raise ValueError('rows must be set when widget is "textarea"')
        return self


class MetaProperty(BaseModel):
    """Represents a meta property in the invoice schema.

    Attributes:
        label (LangLabels): The label of the meta property.
        value_type (Literal["boolean", "integer", "number", "string"]): The type of the value for the meta property.
        description (Optional[str]): The description of the meta property.
        examples (Optional[str]): Examples of the meta property.
        default (Optional[Union[bool, int, float, str]]): The default value for the meta property.
    """

    model_config = ConfigDict(extra="allow")

    label: LangLabels
    value_type: Literal["boolean", "integer", "number", "string"] = Field(..., alias="type")
    description: Optional[str]
    examples: Optional[str]
    default: Optional[Union[bool, int, float, str]]


class CustomItems(RootModel):
    """A class representing custom items in an invoice schema.

    `properties.custom.properties.<custom key>` is an instance of this class.

    Attributes:
        root (dict[str, MetaProperty]): A dictionary containing the custom items.
    """

    root: dict[str, MetaProperty]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class CustomField(BaseModel):
    """Represents a custom field in an invoice schema.

    `properties.custom.` is an instance of this class.
    """

    obj_type: Literal["object"] = Field(..., alias="type")
    label: LangLabels
    required: list[str]
    properties: CustomItems


class TermId(BaseModel):
    const: str


class ClassId(BaseModel):
    const: str


class GeneralChildProperty(BaseModel):
    term_id: TermId = Field(..., alias="termId")


class GeneralProperty(BaseModel):
    object_type: Literal["object"]
    required: list[Literal["termId", "value"]]
    properties: GeneralChildProperty


class SampleGeneralItems(RootModel):
    root: list[GeneralProperty]


class GeneralAttribute(BaseModel):
    """Represents a general attribute in the invoice schema.

    `properties.sample.properties.generalAttribute` is an instance of this class.
    """

    obj_type: Literal["array"] = Field(..., alias="type")
    items: SampleGeneralItems


class SpecificChildProperty(BaseModel):
    term_id: TermId = Field(..., alias="termId")
    class_id: ClassId = Field(..., alias="classId")


class SpecificProperty(BaseModel):
    object_type: Literal["object"]
    required: list[Literal["classId", "termId", "value"]]
    properties: SpecificChildProperty


class SampleSpecificItems(RootModel):
    root: list[SpecificProperty]


class SpecificAttribute(BaseModel):
    """Represents a specific attribute in the invoice schema.

    `properties.sample.properties.specificAttribute` is an instance of this class.
    """

    obj_type: Literal["array"] = Field(..., alias="type")
    items: SampleSpecificItems


class SampleProperties(BaseModel):
    """Represents the properties of a sample.

    `properties.sample.properties` is an instance of this class.

    Attributes:
        general_attribute (Optional[GeneralAttribute]): The general attribute of the sample.
        specific_attribute (Optional[SpecificAttribute]): The Category-specific items of the sample.
    """

    general_attribute: Optional[GeneralAttribute] = Field(..., alias="generalAttribute")
    specific_attribute: Optional[SpecificAttribute] = Field(..., alias="specificAttribute")


class SampleField(BaseModel):
    """Represents a sample field in the invoice schema.

    `properties.sample` is an instance of this class.
    """

    obj_type: Literal["object"] = Field(..., alias="type")
    label: LangLabels
    properties: SampleProperties


class Properties(BaseModel):
    """Represents the properties of an invoice.

    `properties` is an instance of this class.

    Attributes:
        custom (Optional[CustomField]): The custom field of the invoice.
        sample (Optional[str]): A sample field of the invoice.
    """

    custom: Optional[CustomField]
    sample: Optional[str]


class InvoiceSchemaJson(BaseModel):
    """Invoice schema class."""

    version: str = Field(default="https://json-schema.org/draft/2020-12/schema", alias="$schema")
    schema_id: str = Field(..., alias="$id")
    description: str
    value_type: str
    required: Optional[list[Literal["custom", "sample"]]]
    properties: Properties

    @model_validator(mode="after")
    def check_custom_not_none(self):
        """Custom is required but is None."""
        if "custom" in self.required and self.properties.custom is None:
            raise ValueError("custom is required but is None")
        elif "sample" in self.required and self.properties.sample is None:
            raise ValueError("sample is required but is None")
        elif "custom" not in self.required and self.properties.custom:
            raise ValueError("custom is required but is None")
        elif "sample" not in self.required and self.properties.sample:
            raise ValueError("sample is required but is None")
        return self
