from ipywidgets_jsonschema.form import Form, FormError

import jsonschema
import pyrsistent
import pytest


@pytest.mark.parametrize("preconstruct", (0, 1))
def test_form(testcase, preconstruct):
    form = Form(testcase["schema"], preconstruct_array_items=preconstruct)

    # Maybe check that the correct default document was generated
    if "default" in testcase:
        assert pyrsistent.freeze(form.data) == pyrsistent.freeze(testcase["default"])

    # Create all valid documents and double check them
    for doc in testcase.get("valid", []):
        form.data = doc

    # Ensure that invalid documents throw FormError. Note that documents
    # that cannot be validated against the given schema will throw a
    # validation error instead.
    for doc in testcase.get("invalid", []):
        with pytest.raises((FormError, jsonschema.ValidationError)):
            form.data = doc


def test_form_with_descriptions(testcase):
    # simple smoke test to see if generation with descriptions runs withour errors
    Form(testcase["schema"], show_descriptions=True)


def test_add_observer(testcase):
    # Try adding an observer
    form = Form(testcase["schema"])
    form.observe(print, names=("value", "selected_index"), type="change")


@pytest.mark.parametrize("preconstruct", (0, 1))
def test_model_to_json_schema(model, preconstruct):
    schema = model.model_json_schema()
    form = Form(schema, preconstruct_array_items=preconstruct)

    # If a default schema is expected, check the default against the generated data
    if hasattr(model, "default_values") and callable(getattr(model, "default_values")):
        default = model.default_values()
        if default:
            assert pyrsistent.freeze(form.data) == pyrsistent.freeze(default)
    # Validate all valid documents
    for doc in model.valid_cases():
        form.data = doc

    for doc in model.invalid_cases():
        with pytest.raises((FormError, jsonschema.ValidationError)):
            form.data = doc
