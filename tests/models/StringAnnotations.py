from pydantic import BaseModel, Field

class StringWithAnnotations(BaseModel):
    name: str = Field(..., title='Product Name', description='some text')
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"name": "Widget"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"name": 0}]
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"name": ""}