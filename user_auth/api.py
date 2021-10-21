from typing import List
from loguru import logger

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja import Form, Router
from ninja.errors import HttpError

from .scheme import CreateUserSchema, UserSchema, LoginSchema, UpdateUserScheme
from .jwt import create_token, AuthBearer


api_auth = Router(tags=['Authorization'])


@api_auth.post('/login')
def get_token(request, user_form: LoginSchema = Form(...)):
    """Чтобы получить Token, нужно пройти проверку по логину и паролю.

    - 404: пользователь не найден.
    - 401: неверный пароль.
    - 403: Имя должно состоять из одного элемента.

    :return Type Token and Token (действителен с момента создания 1 час).
    """
    user = get_object_or_404(User, username=user_form.username)

    if check_password(user_form.password, user.password):
        logger.info(f'Auth User: {user}.')
        return create_token(user.id)
    else:
        logger.error(f"Password failed verification, "
                     f"User: {user}, "
                     f"Invalid password: {user_form.password}")

        raise HttpError(401, "Invalid password, Please retry later!")


@api_auth.post('/create-user')
def create_user(request, user_item: CreateUserSchema = Form(...)):
    """Регистрация пользователя.
    """

    user = User.objects.create_user(**user_item.dict())
    return create_token(user.id)


@api_auth.get('/{user_id}/user', response=UserSchema, )
def get_user(request, user_id: int):
    """Получить пользователя по ID, требуется Token.
    """
    return get_object_or_404(User, pk=user_id)


@api_auth.get('/users', response=List[UserSchema], auth=AuthBearer())
def get_all_users(request):
    """Получить всех пользователей, требуется Token.
    """
    queryset = User.objects.all()
    return queryset


@api_auth.put('/change-password')
def update_password_user(request, user_form: UpdateUserScheme):
    """Изменение и восстановление пароля.
    - username: Получаем модель пользователя.
    - old_password: Сравниваем старый пароль пользователя.
    - password: Устанавливаем новый пароль пользователя.
    """
    user = get_object_or_404(User, username=user_form.username)
    if check_password(user_form.old_password, user.password):
        user.set_password(user_form.password)
        user.save()
        return {'Success operation': True}
    else:
        raise BaseException
