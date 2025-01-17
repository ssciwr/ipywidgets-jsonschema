from pydantic import BaseModel


class Animal(BaseModel):
    name: str

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"name": "Bello"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return {"name": 231}

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {}


class InheritanceModel(Animal):
    breed: str

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"breed": "Golden Retriever", "name": "Bello"}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return {"name": "Bello"}

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"breed": "", "name": ""}
