import glob
import json
import os


# Read the test data from the schemas subdirectory
_test_data = []
_test_names = []
for filename in glob.glob(
    os.path.join(os.path.split(__file__)[0], "schemas", "*.json")
):
    with open(filename, "r") as f:
        _test_data.append(json.load(f))
        _test_names.append(os.path.basename(filename))


def pytest_generate_tests(metafunc):
    if "testcase" in metafunc.fixturenames:
        metafunc.parametrize("testcase", _test_data, ids=_test_names)
