import glob
import json
import os
import importlib.util
from pydantic import BaseModel

# Read the test data from the schemas subdirectory
_test_data = []
_test_names = []
for filename in glob.glob(
    os.path.join(os.path.split(__file__)[0], "schemas", "*.json")
):
    with open(filename, "r") as f:
        _test_data.append(json.load(f))
        _test_names.append(os.path.basename(filename))
# Import pydantic models from the models subdirectory
models = []
models_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "models/*.py")
for filepath in glob.glob(models_path):
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error loading module {module_name}: {e}")
        continue
    for cls in vars(module).values():
        if (
            isinstance(cls, type)
            and issubclass(cls, BaseModel)
            and cls is not BaseModel
        ):
            models.append(cls)


def pytest_generate_tests(metafunc):
    if "testcase" in metafunc.fixturenames:
        metafunc.parametrize("testcase", _test_data, ids=_test_names)

    if "model" in metafunc.fixturenames:
        metafunc.parametrize("model", models, ids=[model.__name__ for model in models])
