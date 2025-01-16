from pydantic import BaseModel, Field

class StringMinLengthMaxLengthContraint(BaseModel):
    username: str = Field(..., min_length = 3, max_length=30)
    email: str
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"username": "Test", "email" : "user@example.com"}, {"username": "testtesttesttesttest", "email" : "user@example.com"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"name": "te", "email" : "user@example.com"}, {"name": "test", "email" : "userexample.com"}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {}