Architecture Overview
=====================
This document provides an in-depth explanation of the architecture behind the ``Form`` class.
It describes how a form is generated from JSON Schema or Pydantic models.

Overview
--------
The main feature of ``ipywidgets-jsonschema`` is the creation of interactive form widgets directly in Jupyter Notebooks from
JSON Schema or Pydantic model. The widget generation logic is implemented within the Form class in ``ipywidgets_jsonschema/form.py``

The ``Form`` class handles three core tasks:

- **Schema parsing**: Accepts and parses the provided JSON Schema or Pydantic model
- **Widget construction**: Converts parsed schema elements into Jupyter widgets
- **State Management**: Handles data binding, validation and user interaction


Initialization
--------------
Before any widgets are constructed, the provided schema is validated for
correctness using ``jsonschema.validators.Draft7Validator.check_schema()``.
If a Pydantic model is provided, it is first converted to a JSON Schema via ``model.model_json_schema()``.
Then the widget construction is initiated by the recursive method ``_construct()``, which handles schema traversal and widget generation.



FormElement Structure
---------------------
Each field in the form is internally represented as a `FormElement`, a named tuple with:

- ``getter``: retrieves current field value
- ``setter``: assigns a value to the field
- ``resetter``: resets field to default
- ``widgets``: associated ipywidgets components
- ``subelements``: nested FormElements
- ``register_observer``: binds observers to the field

This abstraction allows unified handling of widget state, data extraction, and event registration across different schema types.

Widget construction
-------------------
The function ``_construct(schema)`` handles recursive traversal of the schema. It detects structural keywords such as
``type``, ``enum``, ``anyOf``, ``oneOf``, ``allOf``, ``$ref``, and ``format``.
Each supported type or keyword is dispatched to a dedicated ``_construct_<type>`` handler method.

The following table summarizes the schema features currently supported:

.. list-table::
   :widths: 25 25 55
   :header-rows: 1

   * - Schema Key
     - Handler Method
     - Widget Type
   * - ``type: "string"``
     - ``_construct_string``
     - ``ipywidgets.Text``
   * - ``type: "number"``
     - ``_construct_number``
     - ``FloatText``, ``FloatSlider``
   * - ``type: "integer"``
     - ``_construct_integer``
     - ``IntText``, ``IntSlider``
   * - ``type: "boolean"``
     - ``_construct_boolean``
     - ``Checkbox``
   * - ``type: "object"``
     - ``_construct_object``
     - Nested fields, wrapped in an ``Accordion``
   * - ``type: "array"``
     - ``_construct_array``
     -  subwidgets list
   * - ``enum``
     - ``_construct_enum``
     - ``Dropdown``
   * - ``format``
     - ``_construct_format``
     -  Adds appropiate regex to schema
   * - ``$ref``
     - ``_construct_ref``
     - Recursively resolves definitions from ``$defs``



For nested objects and arrays, ``_construct()`` is called recursively, allowing any complex form to be build from modular schema components.

