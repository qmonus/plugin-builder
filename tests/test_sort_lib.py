import pytest

from qmonus_plugin_builder.libs import sort_lib


@pytest.mark.parametrize('test_data', [
    {
        "args": {
            "ClassA": [],
            "ClassB": [],
            "ClassC": ["ClassF"],
            "ClassD": ["ClassF"],
            "ClassE": [],
            "ClassF": [],
        },
        "expected": ["ClassA", "ClassB", "ClassE", "ClassF", "ClassC", "ClassD"]
    },
    {
        "args": {
            "ClassA": ["ClassD"],
            "ClassB": ["ClassA"],
            "ClassC": ["ClassA"],
            "ClassD": [],
            "ClassE": ["ClassB", "ClassC"],
            "ClassF": ["ClassA"],
        },
        "expected": ["ClassD", "ClassA", "ClassB", "ClassC", "ClassF", "ClassE"]
    },
])
def test_topological_sort_works(test_data: dict):
    results = sort_lib.topological_sort(test_data['args'])
    assert results == test_data['expected']
