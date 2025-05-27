Development - Getting started
=============================

This page explains how to set up the development environment for working on ``ipywidgets-jsonschema``. The goal is to make editing, testing, and experimenting as fast and frictionless as possible.



Setup instructions
------------------
1. Make sure you have the dependencies installed

2. Clone the Repository

.. code-block:: bash

        git clone https://github.com/Suraj3620/ipywidgets-jsonschema.git
        cd ipywidgets-jsonschema

3. Set Up a Virtual Environment (Optional but Recommended)

.. code-block:: bash

        python -m venv .venv
        source .venv/bin/activate

4. Install the package in Editable mode

To avoid reinstalling the package every time you make changes:

.. code-block:: bash

        pip install -e .

This links the installed module directly to your working directory.


5. Live-Reload in Jupyter Notebooks

When developing and testing inside a Jupyter notebook, enable autoreload so code changes are picked up immediately:

.. code-block:: bash

        %load_ext autoreload
        %autoreload 2

You only need to run this once per notebook session. 
Now you can edit files like ``ipywidgets_jsonschema/form.py``, and the updated code will take effect on the next cell execution.