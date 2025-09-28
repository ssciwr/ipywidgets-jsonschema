User API
========

Exceptions
----------

.. autoclass:: ipywidgets_jsonschema.form.FormError
   :members:
   :show-inheritance:

Core
----

.. autoclass:: ipywidgets_jsonschema.form.Form
   :members: __init__, widget, show, data, observe
   :member-order: bysource
   :special-members: __init__
   :show-inheritance:

Pydantic Integration
--------------------

.. autoclass:: ipywidgets_jsonschema.PydanticEditorMixin
   :members:
   :show-inheritance:

Utilities
---------

.. autofunction:: ipywidgets_jsonschema.form.convert_pydantic_to_schema

.. rubric:: Notes

Only the members listed above are considered stable public API. Other objects in
``ipywidgets_jsonschema.form`` are internal.
