import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("../.."))

project = "ipywidgets-jsonschema"
author = "ipywidgets-jsonschema contributors"

try:
    from ipywidgets_jsonschema import __version__
except Exception:
    __version__ = "unknown"

release = __version__
version = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "nbsphinx",
]

autodoc_member_order = "bysource"
autodoc_typehints = "description"

templates_path = ["_templates"]
exclude_patterns = ["_build", "**.ipynb_checkpoints"]

html_theme = "furo"
html_title = "ipywidgets-jsonschema"
html_static_path = ["_static"]
html_css_files = [
    # ipywidgets button icons (icon="...") require Font Awesome classes.
    # We vend these files into _static during the Sphinx build.
    "fontawesomefree/css/all.min.css",
]

# Execute notebooks during docs builds (including Read the Docs)
nbsphinx_execute = "always"
nbsphinx_timeout = 120

master_doc = "index"


def _copy_fontawesome_assets(_app):
    """Copy Font Awesome CSS/webfonts into docs/_static for self-contained builds."""
    try:
        import fontawesomefree
    except ImportError as exc:
        raise RuntimeError(
            "fontawesomefree is required for docs builds. "
            "Install docs requirements before building."
        ) from exc

    package_root = Path(fontawesomefree.__file__).resolve().parent
    source_root = package_root / "static" / "fontawesomefree"
    target_root = Path(__file__).resolve().parent / "_static" / "fontawesomefree"

    (target_root / "css").mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        source_root / "css" / "all.min.css", target_root / "css" / "all.min.css"
    )
    shutil.copytree(
        source_root / "webfonts", target_root / "webfonts", dirs_exist_ok=True
    )


def setup(app):
    app.connect("builder-inited", _copy_fontawesome_assets)
