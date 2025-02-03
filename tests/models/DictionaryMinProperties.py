from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class DictionaryMinProperties(BaseModel):
    name: str
    settings: Dict[str, Optional[Any]] = Field(..., min_properties=1)

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [
             {"name": "Test", "settings": {"key1": 1}},
            {
              "name": "Test",
              "settings": {"key1": 1, "key2": "value", "key3": [1,2,3]}
            },
            {"name": "Test", "settings": {"key1": None}},
           {"name": "Test2", "settings": {"key1": "test"}}
        ]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"name": "Test", "settings": {}}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {}