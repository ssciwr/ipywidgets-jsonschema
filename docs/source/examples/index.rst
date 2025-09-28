.. _examples/index:

Examples
========

This section provides interactive examples of `ipywidgets-jsonschema` in action.

.. toctree::
   :maxdepth: 2
   :caption: Examples:

   Basic Form           <basic_form>
   Pydantic Form        <pydantic_form>

.. admonition:: Advanced: using an explicit JSON Schema
   :class: dropdown

   If you need to inspect or post-process the JSON Schema, you can still pass a schema dict:

   .. code-block:: python

      # Pydantic v2: use model_json_schema() (BaseModel.schema() is deprecated)
      schema = Employee.model_json_schema()

      from ipywidgets_jsonschema.form import Form
      form = Form(schema)
      form.show()
