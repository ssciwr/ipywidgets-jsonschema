from pydantic import BaseModel
from typing import List


class RecursiveModelCategory(BaseModel):
    name: str
    subcategories: List["RecursiveModelCategory"]

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [
            {"name": "Hardware", "subcategories": []},
            {
                "name": "Home",
                "subcategories": [{"name": "Furniture", "subcategories": []}],
            },
        ]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [
            {"name": "Hardware", "subcategories": ["invalid"]},
            {"name": "Home", "subcategories": [{"name": 123}]},
            {"subcategories": []},
        ]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"name": "", "subcategories": []}
