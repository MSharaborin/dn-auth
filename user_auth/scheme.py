from ninja import Schema, ModelSchema
from ninja.errors import HttpError

from pydantic import validator

from django.contrib.auth.models import User


class TokenPayload(Schema):
    user_id: int = None


class LoginSchema(Schema):
    username: str
    password: str

    @validator('username')
    def some_valid_name(cls, username):
        print(len(username.split()))
        if len(username.split()) > 1:
            raise HttpError(403, 'Логин или пароль должен состоять из одного слова..')
        else:
            return username


class CreateUserSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ['username', 'email', 'password']


class UpdateUserScheme(Schema):
    username: str
    old_password: str
    password: str


class UserSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ['id', 'username', 'email']
