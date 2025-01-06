from pydantic import BaseModel


class TestModel(BaseModel):
    """
    Template for creating pydantic models for test cases
    """
    @classmethod
    def valid_cases(cls):
        raise NotImplementedError("Define valid cases in the subclass.")

    @classmethod
    def invalid_cases(cls):
        raise NotImplementedError("Define invalid cases in the subclass.")

    @classmethod
    def default_values(cls):
        raise NotImplementedError("Define default values in the subclass.")