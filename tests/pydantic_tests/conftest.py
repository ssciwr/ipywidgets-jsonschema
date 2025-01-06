# conftest.py
import os
import glob
import importlib.util
from pydantic import BaseModel

def load_models():
    models = []
    models_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "models/*.py")
    for filepath in glob.glob(models_path):
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        #Skip TestModel.py or __init__.py
        if module_name in ("TestModel", "__init__"):
            continue
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        try:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Error loading module {module_name}: {e}")
            continue
        for cls in vars(module).values():
            if isinstance(cls, type) and issubclass(cls, BaseModel) and cls is not BaseModel:
                models.append(cls)

    return models

all_models = load_models()

def pytest_generate_tests(metafunc):
    if "model" in metafunc.fixturenames:
        metafunc.parametrize("model", all_models, ids=[model.__name__ for model in all_models])
