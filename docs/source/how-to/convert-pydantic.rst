.. _how-to/convert-pydantic:

Convert a Pydantic Model to JSON Schema
=========================================

This guide shows you how to convert a Pydantic model to a JSON Schema and use it to create a form.

**1. Define a Pydantic Model**

First, define your Pydantic model:

.. code-block:: python
   :caption: models.py

   from pydantic import BaseModel

   class User(BaseModel):
       name: str
       age: int

**2. Convert the Model to JSON Schema**

Convert the Pydantic model to a JSON Schema and create a form:

.. code-block:: python
   :caption: main.py

   from ipywidgets_jsonschema import form
   from models import User

   schema = User.model_json_schema()
   my_form = form.Form(schema)
   my_form.show()