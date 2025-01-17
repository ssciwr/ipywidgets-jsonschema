from pydantic import BaseModel
from typing import Union, Optional

class UnionStrIntNone(BaseModel):
    value: Optional[Union[str, int]] = None

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [
            {"value": "hello"},
            {"value": 123},
            {"value": None},
            {}
        ]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"value": 123.3}]
 
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {}