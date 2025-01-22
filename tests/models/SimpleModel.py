from pydantic import BaseModel


class SimpleModel(BaseModel):
    id: int
    name: str
    active: bool = True

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"id": 1, "name": "Test", "active": False}, {"id": 2, "name": "Test 2"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"id": "not an int!", "name": "Test", "active": False}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"id": 0, "name": "", "active": True}
