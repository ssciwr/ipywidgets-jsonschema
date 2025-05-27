.. _how-to/customize-form:

Customize the Form
===================

This guide shows you how to customize the Form for better visualization.

**1. Vertically place labels**

You can place the labels vertically instead of horizontally to better represent them.

.. code-block:: python

   from ipywidgets_jsonschema import form
   from models import User

   schema = User.model_json_schema()
   my_form = form.Form(schema, vertically_place_labels=True)
   my_form.show()