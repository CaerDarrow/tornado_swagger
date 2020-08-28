from pydantic import BaseModel, ValidationError, validator, Field
from typing import Optional
from datetime import datetime


class UserModel(BaseModel):
    name: str
    username: str
    password1: str
    password2: str = ...
    date: datetime = datetime.now()

    @validator('name')
    def name_must_contain_space(cls, v):
        if ' ' not in v:
            raise ValueError('must contain a space')
        return v.title()

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError('passwords do not match')
        return v

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v
