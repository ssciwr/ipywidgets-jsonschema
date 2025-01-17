from pydantic import BaseModel, Field


class IntAlias(BaseModel):
    user_id: int = Field(..., alias="id")

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"id": 123}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"id": "not an id"}, {"user_id": 123}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {}
