.. _how-to/add-string-formats:

Add String Formats
==================

This guide shows you how to add string formats to a field to validate it's integrity.

**1. Add the Email format**

You can easily add the email format, which will do all the integrity validations of an email.

.. code-block:: json
   :caption: string_formats_schema.json

   {
        "type": "object",
        "properties": {
            "email": {"type": "string", "format": "email", "title": "Email"}
        }
   }