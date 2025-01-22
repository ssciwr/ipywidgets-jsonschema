from pydantic import BaseModel, Field
from typing import List


class ListUnique(BaseModel):
    ids: List[int] = Field(..., min_items=1, max_items=10, set=True)

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"ids": [1, 2, 3]}, {"ids": [10]}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"ids": []}, {"ids": [1] * 11}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"ids": [0]}
