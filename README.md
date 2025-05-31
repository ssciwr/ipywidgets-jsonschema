# ipywidgets-jsonschema

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ssciwr/ipywidgets-jsonschema/ci.yml?branch=main)](https://github.com/ssciwr/ipywidgets-jsonschema/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/ipywidgets-jsonschema.svg)](https://badge.fury.io/py/ipywidgets-jsonschema)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/ipywidgets-jsonschema.svg)](https://anaconda.org/conda-forge/ipywidgets-jsonschema)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ssciwr/ipywidgets-jsonschema/main?labpath=demo%2Fdemo.ipynb)

A lightweight library that seamlessly combines Pydantic models, JSON Schema, and IPyWidgets to generate interactive, schema‐driven forms in Jupyter notebooks. Define your data models with Pydantic (or raw JSON Schema), and this package will produce validated, dynamic widgets for editing, validation, and serialization.

---

## Features

- **Automatic Widget Generation:** Convert any JSON Schema or Pydantic model into a fully interactive IPyWidgets form.  
- **Pydantic Integration:** Leverage Pydantic’s data validation, typing, and JSON Schema generation.  
- **Nested Structures:** Support for nested objects, arrays, dictionaries, enums, unions, and optional fields.  
- **Schema‐Driven Validation:** Constraints like `minimum`, `maximum`, `regex`, `pattern`, and `enum` are enforced at the widget level.  
- **Layout & Theming Options:** Customize label placement (above or beside inputs), use sliders for numeric fields, pre‐construct array entries, and toggle descriptions.  
- **Inline Editing UI:** The `PydanticEditorMixin` wraps Pydantic models with an “Edit → Save/Cancel” toolbar for in‐place modifications.  
- **JSON Schema Draft 2020-12 Compliance:** Schemas are generated using Pydantic’s built-in support, adhering to the latest draft.  
- **Lightweight & Notebook-Friendly:** No heavyweight dependencies—pure IPyWidgets, Pydantic, and standard Python libraries.

---

![Minimum usage exmaple](https://github.com/Suraj3620/ipywidgets-jsonschema/blob/demo/ipywidgets-jsonschema.gif)

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

## Testing

```
git clone https://github.com/ssciwr/ipywidgets-jsonschema.git
cd ipywidgets-jsonschema
pip install -r requirements-dev.txt
pytest --disable-warnings --maxfail=1 --cov=ipywidgets_jsonschema
```

## Contributing

Please check out Contributing page on the Docs for guidelines on how to contribute, coding style, and best practices. We follow Black for formatting, Flake8 for linting, and MyPy for type checking.

## License

Released under the MIT License. See [LICENSE](https://github.com/ssciwr/ipywidgets-jsonschema/blob/main/LICENSE.md) for details.

