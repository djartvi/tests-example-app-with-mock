import allure
import pytest

from mock_external_service.client import no_token


@allure.feature('Аутентификация')
class TestLogin:
    @allure.title('Логин с валидным токеном')
    @allure.description('Тест проверяет успешную авторизацию с валидным токеном')
    def test_success_login(self, new_client, mock):
        client = new_client()

        mock.stub_auth_success(client.token)

        client.login().assert_success()

        mock.verify_auth_requested(client.token)

    @allure.title('Логин с невалидным токеном')
    @allure.description('Тест проверяет, что авторизация с невалидным токеном возвращает ошибку 400')
    @pytest.mark.parametrize('token', [
        pytest.param('', marks=no_token),
        ' ',
        'SH',
        'ABCDEFGHIJKLMNOPQRSTUVWX12345',
        'ABCDEFGHIJKLMNOPQRSTUVWX1234567',
        'abcdefghijklmnopqrstuvwxyz123456',
        'ABCDEFGHIJKLMNOPQRSTUVWX12345!',
        'ABCDEFGHIJKLMNOPQRSTUVWX12345 ',
        ' ABCDEFGHIJKLMNOPQRSTUVWX12345'
    ])
    def test_login_with_invalid_token(self, new_client, mock, token):
        client = new_client(token)

        client.login().assert_bad_request()

        mock.verify_auth_not_requested(token)

    @allure.title('Логин при существующей сессии')
    @allure.description('Тест проверяет, что разные клиенты могут независимо авторизовываться одновременно')
    def test_login_independent_clients(self, new_client, mock):
        client = new_client()
        second_client = new_client()

        mock.stub_auth_success(client.token)
        mock.stub_auth_success(second_client.token)

        client.login()
        second_client.login().assert_success()

        mock.verify_auth_requested(second_client.token)

    @allure.title('Обработка ошибки внешнего сервиса при логине')
    @allure.description('Тест проверяет обработку ошибки внешнего сервиса при авторизации')
    def test_login_server_error(self, new_client, mock):
        client = new_client()

        mock.stub_auth_server_error(client.token)

        client.login().assert_server_error()
