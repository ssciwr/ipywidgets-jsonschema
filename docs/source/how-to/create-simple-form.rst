.. _how-to/create-simple-form:

Create a Simple Form
====================

This guide shows you how to create a basic form from a JSON Schema.

**1. Define Your JSON Schema**

First, define your JSON Schema:

.. code-block:: json
   :caption: my_schema.json

   {
     "type": "object",
     "properties": {
       "name": {"type": "string", "title": "Name"},
       "age": {"type": "integer", "title": "Age"}
     },
     "required": ["name", "age"]
   }

**2. Load the Schema and Create the Form**

Now, load the schema in Python and create a form:

.. code-block:: python

   import json
   from ipywidgets_jsonschema import form

   with open("my_schema.json", "r") as f:
       my_schema = json.load(f)

   my_form = form.Form(my_schema)
   my_form.show()

This will display an interactive form in your Jupyter Notebook.