from pydantic import BaseModel
from typing import List


class Address(BaseModel):
    street: str
    city: str
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"street": "123 St","city": "New York"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"street": 123,"city": 123}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"street": "","city": ""}

class NestedModelStrings(BaseModel):
    name: str
    addresses: List[Address]
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"name": "Test", "addresses": [{"street": "123 Elm St", "city": "Springfield"}]}, {"name": "Bob", "addresses": [{"street": "123 Elm St", "city": "Springfield"}]}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"name": "Test", "addresses": [{"street": 123, "city": "Springfield"}]}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"name": "", "addresses": [{"street": "","city": ""}]}