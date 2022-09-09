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


def test_add_observer(testcase):
    # Try adding an observer
    form = Form(testcase["schema"])
    form.observe(print, names=("value", "selected_index"), type="change")
