
Code Style & Formatting
=======================
This project enforces consistent code style using pre-commit hooks and the Black code formatter.
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

This sets up a Git hook, so every time you run git commit, the checks are run automatically.

Python
------

Notebook
--------