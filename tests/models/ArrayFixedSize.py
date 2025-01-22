from pydantic import BaseModel, Field, conlist

class ArrayFixedSize(BaseModel):
    fixed_items: conlist(int, min_length=1, max_length=3)
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"fixed_items": [1]},{"fixed_items": [1,2,3]}]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return [{"fixed_items": []},{"fixed_items": [1,2,3,4]}]
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {"fixed_items": [0]}