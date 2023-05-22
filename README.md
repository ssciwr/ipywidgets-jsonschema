# ipywidgets-jsonschema - A widget generator for your Jupyter notebooks

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ssciwr/ipywidgets-jsonschema/ci.yml?branch=main)](https://github.com/ssciwr/ipywidgets-jsonschema/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/ipywidgets-jsonschema.svg)](https://badge.fury.io/py/ipywidgets-jsonschema)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/ipywidgets-jsonschema.svg)](https://anaconda.org/conda-forge/ipywidgets-jsonschema)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ssciwr/ipywidgets-jsonschema/main?labpath=demo%2Fdemo.ipynb)

## Usage

![Minimum usage exmaple](https://raw.githubusercontent.com/ssciwr/ipywidgets-jsonschema/main/ipywidgets-jsonschema.gif)

This project allows you to generate Jupyter widgets from schemas
that follow the [JSONSchema specification](https://json-schema.org). If you already have
a schema available, creating a widget form for it is as simple
as this:


```
from ipywidgets_jsonschema import Form
form = Form(schema)
form.show()
```

The data can then be retrieved from `form` by accessing `form.data`.

## Features

These are the core features:

* Generation of `ipywidgets` widgets for all basic types
* Read and write access to the current document state

## Installation

`ipywidgets-jsonschema` can be installed with pip:

```
python -m pip install ipywidgets-jsonschema
```

Alternatively, you can get it from `conda-forge`:

```
conda install -c conda-forge ipywidgets-jsonschema
```

## Known limitations

* Some aspects of the JSON Schema specification are hard to implement in
  a form generator and are therefore omitted e.g.
  * The `allOf` and `not` rules for schema composition are only partially or not at all supported.
  * Media types
  * There is only rudimentary support for conditional subschemas (like `if`-`then`-`else`)
* Some annotations that are purely optional in the specification are required
  for the schema to be usable with `ipywidgets-jsonschema` e.g. a `title` field
  when the resulting widget would otherwise not be self-explanatory.
