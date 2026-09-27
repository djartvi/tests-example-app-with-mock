import allure
import pytest


@allure.feature('Действия авторизованного пользователя')
class TestAction:
    @allure.title('Запрос на выполнение действия')
    @allure.description('Тест проверяет, что действия доступны после авторизации')
    def test_action(self, new_client, mock):
        client = new_client()

        mock.stub_auth_success(client.token)
        mock.stub_do_action_success(client.token)

        client.login()
        client.action()

        mock.verify_auth_requested(client.token)
        mock.verify_do_action_requested(client.token)

    @allure.title('Запрос на выполнение действия незалогиненного пользователя')
    @allure.description('Тест проверяет, что действия не доступны без авторизации')
    def test_action_forbidden(self, new_client, mock):
        client = new_client()

        client.action().assert_forbidden()

        mock.verify_do_action_not_requested(client.token)

    @allure.title('Обработка ошибки внешнего сервиса при запросе действия')
    @allure.description('Тест проверяет, что приложение обрабатывает ошибки внешнего сервиса')
    def test_action_server_error(self, new_client, mock):
        client = new_client()

        mock.stub_auth_success(client.token)
        mock.stub_do_action_server_error(client.token)
        
        client.login()

        client.action().assert_server_error
    @allure.title('Действия для независимых клиентов')
    @allure.description('Тест проверяет, может ли приложение работать с несколькими залогиненными клиентами')
    def test_action_for_independent_clients(self, new_client, mock):
        client = new_client()
        second_client = new_client()

        for each in (client, second_client):
            mock.stub_auth_success(each.token)
            mock.stub_do_action_success(each.token)
            each.login()

        second_client.action().assert_success()
        mock.verify_do_action_requested(second_client.token)

        client.action().assert_success()
        mock.verify_do_action_requested(client.token)

    @allure.title('Запрос некорректного действия')
    @allure.description('Тест проверяет, что клиенту доступны только определённые действия')
    @pytest.mark.parametrize('action', [
        'DO', 'DOACTION', 'DELETE', 'ENDPOINT', 'login', 'action', 'logout',
        ' ', '', 'LOG IN', 'LOGIN ', ' LOGIN', 'LOGIN\n', 'LOGIN\t',
        'LOGIN_', 'LOGIN-', 'LOGIN.ACTION', 'LOGIN;ACTION', 'ЛОГИН',
        '123456', '@#$%^&*', 'LOGINACTION'
    ])
    def test_incorrect_action_request(self, new_client, mock, action):
        client = new_client()

        mock.stub_auth_success(client.token)

        client.login()
        client.custom_request(action=action).assert_bad_request()

        mock.verify_do_action_not_requested(client.token)
