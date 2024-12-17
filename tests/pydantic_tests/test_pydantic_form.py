from ipywidgets_jsonschema.form import Form, FormError

from pydantic import BaseModel, ValidationError
import pytest
import pyrsistent
import jsonschema
from jsonschema import Draft202012Validator


class SimpleModel(BaseModel):
    id: int
    name:str
    active: bool = True



TEST_CASES = [
    {
        "model": SimpleModel,
        "valid": [{"id": 1, "name": "Test", "active": False}, {"id": 2, "name": "Test 2"}],
        "invalid":[{"id": "not an int!", "name": "Test", "active": False}],
        "default": {"active": True},
    },
]


@pytest.mark.parametrize("testcase", TEST_CASES)
@pytest.mark.parametrize("preconstruct", (0,1))
def test_model_to_json_schema(testcase, preconstruct):
    model = testcase["model"]
    schema = model.model_json_schema()

    form = Form(schema, preconstruct_array_items=preconstruct)

    #If a default schema is expected, check the default against the generated data
    if "default" in testcase:
        assert pyrsistent.freeze(form.data) == pyrsistent.freeze(testcase["default"])

    #Validate all valid documents
    for doc in testcase.get("valid",[]):
        form.data = doc
    
    for doc in testcase.get("invalid", []):
        with pytest.raises((FormError, jsonschema.ValidationError)):
            form.data = doc

    




