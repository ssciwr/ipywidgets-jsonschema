from pydantic import BaseModel


class DictionaryModel(BaseModel):
    name: str
    settings: dict[str, int]

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"name": "Test", "settings": {"key1": 1}}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"name": "Test", "settings": {}}, {"name": "Test"}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"name": "", "settings": {}}
