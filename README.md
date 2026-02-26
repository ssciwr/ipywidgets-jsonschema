# ipywidgets-jsonschema

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ssciwr/ipywidgets-jsonschema/ci.yml?branch=main)](https://github.com/ssciwr/ipywidgets-jsonschema/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/ipywidgets-jsonschema.svg)](https://badge.fury.io/py/ipywidgets-jsonschema)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/ipywidgets-jsonschema.svg)](https://anaconda.org/conda-forge/ipywidgets-jsonschema)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ssciwr/ipywidgets-jsonschema/main?labpath=demo%2Fdemo.ipynb)

A lightweight library that seamlessly combines Pydantic models, JSON Schema, and IPyWidgets to generate interactive, schema‐driven forms in Jupyter notebooks. Define your data models with Pydantic (or raw JSON Schema), and this package will produce Jupyter widgets for editing and validating.

---

## Features

- **Automatic Widget Generation:** Convert any JSON Schema or Pydantic model into a fully interactive IPyWidgets form.
- **Pydantic Integration:** Leverage Pydantic’s data validation, typing, and JSON Schema generation.
- **Nested Structures:** Support for nested objects, arrays, dictionaries, enums, unions, and optional fields.
- **Inline Editing UI:** The `PydanticEditorMixin` wraps Pydantic models with an “Edit → Save/Cancel” toolbar for in‐place modifications.

---

## Installation

`ipywidgets-jsonschema` can be installed with pip:

```
python -m pip install ipywidgets-jsonschema
```

Alternatively, you can get it from `conda-forge`:

```
conda install -c conda-forge ipywidgets-jsonschema
```

## Quick Start

```
from pydantic import BaseModel, Field
from ipywidgets_jsonschema import Form

class Person(BaseModel):
    name: str = Field(..., description="Your full name")
    age: int = Field(..., ge=0, description="Your age in years")
    email: str = Field(None, description="Optional email")

form = Form(Person)
form.show()

# Interact with the form in Jupyter; retrieve validated data:
print(form.data)  # e.g. {"name": "Alice", "age": 30, "email": "alice@example.com"}
```

That’s it—your Pydantic model is now an interactive form. For more advanced examples (nested models, enums, unions, customization), see the Documentation.


## License

Released under the MIT License.
