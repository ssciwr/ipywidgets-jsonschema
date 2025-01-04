from ipywidgets_jsonschema.form import Form, FormError
from pydantic import BaseModel, ValidationError
import pytest
import pyrsistent
import jsonschema
from jsonschema import Draft202012Validator


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



TEST_CASES = [SimpleModel]


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


