from ipywidgets_jsonschema.form import Form, FormError
from pydantic import BaseModel, ValidationError
import pytest
import pyrsistent
import jsonschema
from jsonschema import Draft202012Validator
import glob
import importlib.util
import os



from datetime import datetime
from typing import List
from pydantic import Field
from typing import Literal
from pydantic import conint, conlist
from enum import Enum
from typing import List
from typing import Annotated
from uuid import UUID
from typing import Union, Dict
from typing import TypeVar, Generic
from pydantic.networks import IPvAnyAddress
from pydantic import Json
from typing import Optional
from pydantic import PrivateAttr
from typing import Any
from typing import List
class BaseTestModel(BaseModel):

    #Decorator used in case for inheritance
    @classmethod
    def valid_cases(cls):
        pass
    @classmethod
    def invalid_cases(cls):
        pass
    @classmethod
    def default_values(cls):
        pass


class SimpleModel(BaseModel):
    id: int
    name: str
    active: bool = True

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"id": 1, "name": "Test", "active": False}, {"id": 2, "name": "Test 2"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"id": "not an int!", "name": "Test", "active": False}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {'id': 0, 'name': '','active': True}


class Address(BaseModel):
    street: str
    city: str
class StringNested(BaseModel):
    name: str
    addresses: List[Address]
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"name": "Test", "addresses": [{"street": "123 Elm St", "city": "Springfield"}]}, {"name": "Bob", "addresses": [{"street": "123 Elm St", "city": "Springfield"}]}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"name": "Test", "addresses": [{"street": 123, "city": "Springfield"}]}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"name": "", "addresses": [{"street": "","city": ""}]}
class StringAndInt(BaseModel):
    name: str
    age: int
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"name": "Test", "age" : 20}, {"name": "Bob", "age" : 33}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"name": "Test", "age" : "20"}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"name": "", "age" : 0}

class StringMinLengthMaxLengthContraint(BaseModel):
    username: str = Field(..., min_length = 3, max_length=30)
    email: str = Field(..., format='email')
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"username": "Test", "email" : "user@example.com"}, {"username": "testtesttesttesttest", "email" : "user@example.com"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"name": "te", "email" : "user@example.com"}, {"name": "test", "email" : "userexample.com"}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {}
class FloatMultipleOfMinumumContraint(BaseModel):
    price: float = Field(..., multiple_of = 0.5, minimum = 0.0)
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"price": 10.0}, {"price" : 0.5}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"price": -1.0}, {"price" : 1.3}]
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"price": 0.0}

class StringRegex(BaseModel):
    username: str = Field(max_length=30, pattern='^[a-zA-Z0-9_]+$')
    email: str = Field(format='email')
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"username": "Test_123", "email": "user@example.com"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"username": "Invalid username ", "email": "userexample.com"}]
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"username": "username", "email": "example@example.com"}


class Group(BaseModel):
    ids: List[int] = Field(..., min_items = 1, max_items = 10, set = True)
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"ids" : [1, 2, 3]}, {"ids" : [10]}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"ids" : []}, {"ids" : [1] * 11 }]
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"ids" : [0]}

class DictMinProperties(BaseModel):
    name: str
    settings: dict[str, int]
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"name": "Test", "settings" : {"key1" : 1}}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"name": "Test", "settings" : {}}, {"name": "Test"}]
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"name": "", "settings" : {}}

class StringWithAnnotations(BaseModel):
    name: str = Field(..., title='Product Name', description='some text')
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"name": "Widget"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"name": 0}]
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"name": ""}

class FixedArraySize(BaseModel):
    fixed_items: conlist(int, min_length=1, max_length=3)
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"fixed_items": [1]},{"fixed_items": [1,2,3]}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"fixed_items": []},{"fixed_items": [1,2,3,4]}]
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"fixed_items": [0]}

class IntAlias(BaseModel):
    user_id: int = Field(..., alias = 'id' )

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"id": 123 }]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"id": "not an id"}, {"user_id" : 123}]
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {}

class StringPrivateField(BaseModel):
    _password: str = PrivateAttr()
    _private_password: str
    def __init__(self, password : str):
        self._password = password
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"password" : "securepassword" }]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return []
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {}
    

class Animal(BaseModel):
    name: str

class Dog(Animal):
    breed: str
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"breed" : "Golden Retriever" , "name": "Bello"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return {"name": "Bello"}

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"breed" : "" , "name": ""}


class Category(BaseModel):
    name: str
    subcategories: List['Category']
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"name" : "Hardware", "subcategories": []},{"name" : "Home", "subcategories": [{"name" : "Furniture", "subcategories" : []}]}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"name" : "Hardware", "subcategories": ["invalid"]},
                 {"name" : "Home", "subcategories": [{"name" : 123}]},
                 {"subcategories": []} 
                ]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return  {"subcategories": []} 



class LiteralModel(BaseModel):
    category: Literal['clothing' , 'food' ]
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"category" : "clothing"},{"category" : "food"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"category" : "hardware"},{"category" :123}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {}



class Color(Enum):
    RED = 'red'
    BLUE = 'blue'
    GREEN = 'green'

class ListEnum(BaseModel):
    colors: List[Color]
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"colors" :["red", "blue"]}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"colors" :["red", "yellow"]}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return [{"colors" :[]}]

class ModelAnnotated(BaseModel):
    #Please note there is no check up 
    username: Annotated[str, 'Must be 12 characters', 'Must be alphanumeric']
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"username" : "ValidUser12"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"username" : 0000}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"username" : ""}

class UUIDModel(BaseModel):
    event_id: UUID


class Item(BaseModel):
    price: Union[int, float]
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"price" : 10}, {"price" : 9.99}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"price" : "10"}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return [{"price" : 0}]

    
class UnionIntFloat(BaseModel):
    price: int | float
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"price" : 10}, {"price" : 9.99}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"price" : "10"}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return [{"price" : 0}]

class DictUnion(BaseModel):
    settings: Dict[str, Union[int, str]]
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"settings" : {"key1": 10, "key2" : "value"}}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"settings" : {"key1": 10, "key2" : ["value"]}}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return [{"settings" : {}}]

T = TypeVar('T')
class Generics(BaseModel, Generic[T]):
    data: T
    status: int
    message: str
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"data": "Example data", "status": 200, "message": "Success"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"data": None, "status": "ok", "message": "Fail"}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return [{"data": None, "status": 0, "message": ""}]
class IpModel(BaseModel):
    ip: IPvAnyAddress
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"ip": "192.168.1.1"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"ip": 0}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"ip": ""}

class DynamicConfig(BaseTestModel):
    raw_json: Json
    metadata: Dict[str, Any]
    settings_json: Json[Dict[str, Any]]

    @classmethod
    def valid_cases(cls):
        return [
            {
                "raw_json": '{"key": "value"}',
                "metadata": {"version": 1},
                "settings_json": '{"setting": 42}',
            },
        ]

    @classmethod
    def invalid_cases(cls):
        return [
            {"raw_json": 123},
            {"metadata": "not a dict"},
            {"settings_json": '{"setting": "not an int"}'},
        ]

    @classmethod
    def default_values(cls):
        return {
            "raw_json": "{}",
            "metadata": {},
            "settings_json": "{}",
        }  # Empty JSON and dicts as defaults



class OptionalModel(BaseTestModel):
    field1: Optional[str] = None
    field2: Optional[int] = None
    field3: Optional[List[str]] = None

    @classmethod
    def valid_cases(cls):
        return [
            {},  
            {"field1": "Test", "field2": 10, "field3": ["item1", "item2"]},
            {"field1": None, "field2": None, "field3": None}, 
        ]

    @classmethod
    def invalid_cases(cls):
        return [
            {"field1": 123},
            {"field2": "not an int"},
            {"field3": "not a list"},
        ]

    @classmethod
    def default_values(cls):
        return {"field1": None, "field2": None, "field3": None}  # All fields default to `None`

TEST_CASES = [
    SimpleModel, StringNested, StringAndInt, StringMinLengthMaxLengthContraint, FloatMultipleOfMinumumContraint,
    StringRegex, Group,DictMinProperties,StringWithAnnotations,FixedArraySize,IntAlias,StringPrivateField,Dog,Category,LiteralModel,
    ListEnum, ModelAnnotated, Item, UnionIntFloat, DictUnion, Generics, IpModel,DynamicConfig, OptionalModel
]
@pytest.mark.parametrize("model", TEST_CASES)
@pytest.mark.parametrize("preconstruct", (0, 1))
def test_model_to_json_schema(model, preconstruct):
    schema = model.model_json_schema()
    form = Form(schema, preconstruct_array_items=preconstruct)

    #If a default schema is expected, check the default against the generated data
    default = model.default_values()
    if default:
        assert pyrsistent.freeze(form.data) == pyrsistent.freeze(default)

    # Validate all valid documents
    for doc in model.valid_cases():
        form.data = doc

    for doc in model.invalid_cases():
        with pytest.raises((FormError, jsonschema.ValidationError)):
            form.data = doc


