from pydantic import BaseModel
from typing import TypeVar, Generic

T = TypeVar('T')
class Generics(BaseModel, Generic[T]):
    data: T
    status: int
    message: str
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"data": "Example data", "status": 200, "message": "Success"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"data": None, "status": "ok", "message": "Fail"}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return [{"data": None, "status": 0, "message": ""}]