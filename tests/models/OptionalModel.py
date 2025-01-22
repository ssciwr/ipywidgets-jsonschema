from pydantic import BaseModel
from typing import Optional, List


class OptionalModel(BaseModel):
    field1: Optional[str] = None
    field2: Optional[int] = None
    field3: Optional[List[str]] = None

    @classmethod
    def valid_cases(cls):
        return [
            {},
            {"field1": "Test", "field2": 10, "field3": ["item1", "item2"]},
            {"field1": None, "field2": None, "field3": None},
        ]

    @classmethod
    def invalid_cases(cls):
        return [
            {"field1": 123},
            {"field2": "not an int"},
            {"field3": "not a list"},
        ]

    @classmethod
    def default_values(cls):
        return {"field1": "", "field2": 0, "field3": []}
