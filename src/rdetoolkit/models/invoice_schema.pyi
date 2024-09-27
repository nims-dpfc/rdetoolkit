from _typeshed import Incomplete
from pydantic import BaseModel, RootModel
from typing import Literal, Optional, Union

class LangLabels(BaseModel):
    ja: str
    en: str

class Placeholder(BaseModel):
    ja: str
    en: str

class Options(BaseModel):
    widget: Optional[Literal['textarea']]
    rows: Optional[int]
    unit: Optional[str]
    placeholder: Optional[Placeholder]

class MetaProperty(BaseModel):
    model_config: Incomplete
    label: LangLabels
    value_type: Literal['boolean', 'integer', 'number', 'string']
    description: Optional[str]
    examples: Optional[list[Union[bool, int, float, str]]]
    default: Optional[Union[bool, int, float, str]]
    const: Optional[Union[bool, int, float, str]]
    enum: Optional[list[Union[bool, int, float, str]]]
    maximum: Optional[int]
    exclusiveMaximum: Optional[int]
    minimum: Optional[int]
    exclusiveMinimum: Optional[int]
    maxLength: Optional[int]
    minLength: Optional[int]
    pattern: Optional[str]
    format: Optional[Literal['date', 'time', 'uri', 'uuid', 'markdown']]

class CustomItems(RootModel):
    root: dict[str, MetaProperty]
    def __iter__(self): ...
    def __getitem__(self, item): ...

class CustomField(BaseModel):
    obj_type: Literal['object']
    label: LangLabels
    required: list[str]
    properties: CustomItems

class TermId(BaseModel):
    const: str

class ClassId(BaseModel):
    const: str

class GeneralChildProperty(BaseModel):
    term_id: TermId

class GeneralProperty(BaseModel):
    object_type: Literal['object']
    required: list[Literal['termId', 'value']]
    properties: GeneralChildProperty

class SampleGeneralItems(RootModel):
    root: Optional[list[GeneralProperty]]

class GeneralAttribute(BaseModel):
    obj_type: Literal['array']
    items: SampleGeneralItems

class SpecificChildProperty(BaseModel):
    term_id: TermId
    class_id: ClassId

class SpecificProperty(BaseModel):
    object_type: Literal['object']
    required: list[Literal['classId', 'termId', 'value']]
    properties: SpecificChildProperty

class SampleSpecificItems(RootModel):
    root: list[SpecificProperty]

class SpecificAttribute(BaseModel):
    obj_type: Literal['array']
    items: SampleSpecificItems

class BasicItemsValue(BaseModel):
    value_type: Union[str, list, None]
    format: Optional[Literal['date']]
    pattern: Optional[str]
    description: Optional[str]

class SamplePropertiesWhenAdding(BaseModel):
    sample_id: Optional[str]
    ownerId: str
    composition: Optional[str]
    referenceUrl: Optional[str]
    description: Optional[str]
    generalAttributes: Optional[GeneralAttribute]
    specificAttributes: Optional[SpecificAttribute]

class SampleProperties(BaseModel):
    generalAttributes: Optional[GeneralAttribute]
    specificAttributes: Optional[SpecificAttribute]

class SampleField(BaseModel):
    obj_type: Literal['object']
    label: LangLabels
    required: list[Literal['names', 'sampleId']]
    properties: SampleProperties

class BasicItems(BaseModel):
    dateSubmitted: BasicItemsValue
    dataOwnerId: BasicItemsValue
    dateName: BasicItemsValue
    instrumentId: Optional[BasicItemsValue]
    experimentId: Optional[BasicItemsValue]
    description: Optional[BasicItemsValue]

class DatasetId(BaseModel):
    value_type: str

class Properties(BaseModel):
    custom: Optional[CustomField]
    sample: Optional[SampleField]

class InvoiceSchemaJson(BaseModel):
    model_config: Incomplete
    version: str
    schema_id: str
    description: Optional[str]
    value_type: Literal['object']
    required: Optional[list[Literal['custom', 'sample']]]
    properties: Properties
