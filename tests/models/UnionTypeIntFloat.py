from pydantic import BaseModel
from typing import Union
class UnionTypeIntFloat(BaseModel):
    price: Union[int, float]
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"price" : 10}, {"price" : 9.99}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"price" : "10"}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return [{"price" : 0}]