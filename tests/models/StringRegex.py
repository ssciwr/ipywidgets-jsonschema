from pydantic import BaseModel, Field


class StringRegex(BaseModel):
    username: str = Field(max_length=30, pattern="^[a-zA-Z0-9_]+$")
    email: str = Field(format="email")

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"username": "Test_123", "email": "user@example.com"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"username": "Invalid username ", "email": "userexample.com"}]
