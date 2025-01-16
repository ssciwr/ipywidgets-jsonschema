from pydantic import BaseModel
from typing import Annotated
class ModelAnnotated(BaseModel):
    #Please note there is no check up 
    username: Annotated[str, 'Must be 12 characters', 'Must be alphanumeric']
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"username" : "ValidUser12"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"username" : 0000}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"username" : ""}