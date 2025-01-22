from pydantic import BaseModel
from typing import Json, Dict, Any


class JsonModel(BaseModel):
    raw_json: Json
    metadata: Dict[str, Any]
    settings_json: Json[Dict[str, Any]]

    @classmethod
    def valid_cases(cls):
        return [
            {
                "raw_json": '{"key": "value"}',
                "metadata": {"version": 1},
                "settings_json": '{"setting": 42}',
            },
        ]

    @classmethod
    def invalid_cases(cls):
        return [
            {"raw_json": 123},
            {"metadata": "not a dict"},
            {"settings_json": '{"setting": "not an int"}'},
        ]

    @classmethod
    def default_values(cls):
        return {
            "raw_json": "{}",
            "metadata": {},
            "settings_json": "{}",
        }  # Empty JSON and dicts as defaults
