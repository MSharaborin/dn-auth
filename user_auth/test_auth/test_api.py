import pytest
from ..jwt import create_token


@pytest.mark.django_db
@pytest.fixture
def user(django_user_model):
    user = django_user_model.objects.create_user(
        'john',
        'lennon@thebeatles.com',
        'johnpassword'
    )
    return user


class TestAuthApi:

    @pytest.mark.django_db
    def test_checked_user(self, user, django_user_model):
        """Тест создает пользователя и удаляет его.
        """
        assert django_user_model.objects.count() == 1

    def test_get_url_docs(self, client):
        url = '/api/v1/docs'
        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    @pytest.mark.parametrize('username, password, status_code', [
        ('john', 'johnpassword', 200),
        ('john', '57669', 401),
        ('asdasd', 1231, 404),
        ('aa aa', 'aaa', 403)
    ])
    def test_checked_status_code_api_login(
            self, client, username, password, status_code, user
    ):
        url = '/api/v1/auth/login'
        data = {
            'username': username,
            'password': password
        }
        response = client.post(url, data)
        assert response.status_code == status_code

    @pytest.mark.django_db
    def test_get_token(self, user):
        token = create_token(user.id)
        response = token.get('Authorization')
        assert response is not None

    @pytest.mark.django_db
    @pytest.mark.parametrize('login, password, email, status_code', [
        ('user1', 'password1', 'user1@mail.com', 200),
        # ('admin', '', '', 404), TODO продолжить тестирование после модели пользователя
        # ('user1', '', 'user1', 500),
    ])
    def test_create_user_api(self, client, login, password, email, status_code):
        url = '/api/v1/auth/create-user'

        data = {
            'username': login,
            'email': email,
            'password': password
        }
        response = client.post(url, data)
        assert response.status_code == status_code

    @pytest.mark.django_db
    def test_get_user_and_users(self, client, user):
        url_user = f'/api/v1/auth/{user.id}/user'
        url_users = '/api/v1/auth/users'

        headers = create_token(user.id)

        response_user = client.get(url_user)
        response_users = client.get(url_users, headers=headers)

        assert response_user.status_code == 200
        assert response_users.status_code == 200
