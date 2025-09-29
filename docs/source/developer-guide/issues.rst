Limitations and known issues
============================
There are some known limitations both due to the current implementation and the design of ``JSON Schema`` itself.


Custom Validation not supported
-------------------------------
Custom validators (``@validator``, ``@field_validator``) in Pydantic models have no effect on the generated form.
Runtime validation will still catch errors, but the form itself does not enforce these rules.


No Support for generics or parametrized Models
----------------------------------------------
Pydantic generics (e.g. ``List[T]``) are not supported,as they cannot be fully resolved into standalone schemas without type information.


Architecture Notes
------------------
Currently, the core functionality of ``ipywidgets-jsonschema`` is implemented inside a single file:
``ipywidgets_jsonschema/form.py``.

This file contains the main Form class, which is responsible for:

- Parsing the JSON Schema or Pydantic model
- Building all widgets


This design keeps things simple and centralized, but comes with some tradeoffs:
- All widget construction logic in one place


- Makes future refactoring more complex
