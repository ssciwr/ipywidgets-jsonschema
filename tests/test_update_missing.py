from ipywidgets_jsonschema.form import deep_update_missing


def test_update_missing_insert():
    target = {"A": 1}
    source = {"B": 2}
    result = deep_update_missing(target, source)
    assert result["B"] == 2


def test_update_missing_ignore():
    target = {"A": 1}
    source = {"A": 2}
    result = deep_update_missing(target, source)
    assert result["A"] == 1


def test_update_missing_deep_insert():
    target = {
        "A": {
            "B": {"E": 4},
        }
    }
    source = {"A": {"B": {"E": 3, "F": 5}, "E": 4}}
    result = deep_update_missing(target, source)
    assert result["A"]["B"]["E"] == 4
    assert result["A"]["B"]["F"] == 5
    assert result["A"]["E"] == 4
