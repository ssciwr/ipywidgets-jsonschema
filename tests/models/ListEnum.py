from pydantic import BaseModel
from typing import Enum, List
class Color(Enum):
    RED = 'red'
    BLUE = 'blue'
    GREEN = 'green'

class ListEnum(BaseModel):
    colors: List[Color]
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"colors" :["red", "blue"]}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"colors" :["red", "yellow"]}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return [{"colors" :[]}]