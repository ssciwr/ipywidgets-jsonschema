from ipywidgets_jsonschema import Form


def test_form(testcase):
    form = Form(testcase["schema"])
    form.data
