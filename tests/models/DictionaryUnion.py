from pydantic import BaseModel
from typing import Dict, Union


class DictUnion(BaseModel):
    settings: Dict[str, Union[int, str]]

    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"settings": {"key1": 10, "key2": "value"}}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"settings": {"key1": 10, "key2": ["value"]}}]

    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"settings": {}}
