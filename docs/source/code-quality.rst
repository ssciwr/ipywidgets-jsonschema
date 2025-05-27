
Code Style & Formatting
=======================
This project enforces consistent code style using pre-commit hooks and the ``Black`` code formatter.
The goal is to keep the codebase clean, readable and consistent.


Pre-commit Setup
----------------
We use `pre-commit` to automatically format and lint code before it's commited.

1. Install pre-commit

.. code-block:: bash

        pip install pre-commit

2. Install the hooks:

From the project root, run:

.. code-block:: bash

        pre-commit install

This sets up a Git hook, so every time you run git commit, the configured checks are run automatically.

To run all checks manually:

.. code-block:: bash

    pre-commit run --all-files


Python
------
Python code is automatically formatted using `Black <https://black.readthedocs.io/>`_, a PEP 8 compliant opinionated formatter.
We use the ``black-jupyter`` hook, which supports both ``.py`` and code cells in notebooks.

**What gets checked**:

- Formatting
- Trailing whitespace cleanup
- Validation of ``YAML`` and ``JSON`` files.


Jupyter
--------
We include automatic cleanup and formatting for Jupyter notebooks:

- ``nbstripout`` removes output cells before committing, keeping diffs clean.
- ``black-jupyter`` formats code inside notebooks using Black.



