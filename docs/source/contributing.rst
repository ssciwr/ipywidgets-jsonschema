.. _contributing:

Contributing
============

Thank you for considering contributing to `ipywidgets-jsonschema`!  We welcome contributions of all kinds.

**How to Contribute:**

1.  **Fork the repository** on GitHub.

2.  **Create a branch** for your changes:  `git checkout -b my-feature-branch`

3.  **Make your changes.**

4.  **Write tests** for your changes.  We use `pytest` for testing.

5.  **Run the tests:**  `pytest`

6.  **Format your code:** We use `black` and `isort`. Run `black .` and `isort .`

7.  **Commit your changes:** `git commit -m "Add my feature"`

8.  **Push to your fork:** `git push origin my-feature-branch`

9.  **Create a pull request** on GitHub.

**Adding New Features:**

*   If you're adding a new feature, please open an issue first to discuss it.
*   When adding new features, it's necessary to add a `testcase` to test it in the `test_form.py` in the test suite. This can be a `.json` file with a schema in the `/schemas` directory, and a corresponding model written with pydantic and added to the `/models` directory with the name `<model_name>.py`. If the class is a subclass of the class `BaseModel`, this can be converted automatically.
*   Make sure your code adheres to the project's coding style.
*   Write clear and concise docstrings for all new functions and classes.

**Adding a New Notebook example:**

1. Add the new notebook example to the `/examples` directory.
2. Add the notebook to the corresponding `toctree` in the `index.rst` file.

**Reporting Bugs:**

*   If you find a bug, please open an issue on GitHub.
*   Include a clear description of the bug, steps to reproduce it, and any relevant error messages.

**Documentation:**

*   Keep the documentation concise and add a clear description of what the function does, including example where possible.
*   When adding documentation in the `docs/source` directory, add the file to the `toctree` in `index.rst` to have it appear in the documentation.