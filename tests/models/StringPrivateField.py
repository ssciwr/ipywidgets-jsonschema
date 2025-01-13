from pydantic import BaseModel, PrivateAttr

class StringPrivateField(BaseModel):
    _password: str = PrivateAttr()
    _private_password: str
    def __init__(self, password : str):
        self._password = password
    @classmethod
    def valid_cases(cls):
        """Provide valid cases for the model."""
        return [{"password" : "securepassword" }]

    @classmethod
    def invalid_cases(cls):
        """Provide invalid cases for the model."""
        return []
    @classmethod
    def default_values(cls):
        """Provide default values for the model."""
        return {}