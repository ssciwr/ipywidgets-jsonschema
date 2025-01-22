from pydantic import BaseModel, Field

class FloatMultipleOfMinumumContraint(BaseModel):
    price: float = Field(..., multiple_of = 0.5, minimum = 0.0)
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"price": 10.0}, {"price" : 0.5}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"price": -1.0}, {"price" : 1.3}]
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"price": 0.0}