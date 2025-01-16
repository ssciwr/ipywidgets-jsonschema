from pydantic import BaseModel
from typing import Literal

class Literals(BaseModel):
    category: Literal['clothing' , 'food' ]
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"category" : "clothing"},{"category" : "food"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"category" : "hardware"},{"category" :123}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {}