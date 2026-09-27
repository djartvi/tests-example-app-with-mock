import allure
import pytest

from base.app_client import Action
from mock_external_service.client import no_token


@allure.feature('Обработка некорректных запросов')
class TestEndpointNegative:
    @allure.title('Запрос без параметра token')
    @allure.description('Тест проверяет, что для LOGIN, ACTION и LOGOUT запрос без токена возвращает ошибку 400')
    @no_token
    @pytest.mark.parametrize('action', list(Action))
    def test_no_token_in_request(self, new_client, mock, action):
        new_client().request_without_token(action).assert_bad_request()

        mock.verify_auth_not_requested()
        mock.verify_do_action_not_requested()

    @allure.title('Запрос без параметра action')
    @allure.description('Тест проверяет обработку запроса без параметра action')
    def test_no_action_in_request(self, new_client, mock):
        client = new_client()

        client.request_without_action().assert_bad_request()

        mock.verify_auth_not_requested(client.token)
        mock.verify_do_action_not_requested(client.token)

    @allure.title('Запрос по неверному адресу')
    @allure.description('Тест проверяет обработку запроса по неверному адресу')
    @pytest.mark.parametrize('path', [
        '/wrong', '/endpoint123', '/endpoint/login', '/endpoint/action', '/endpoin', '/endpoints', ''
    ])
    def test_incorrect_endpoint_request(self, new_client, mock, path):
        client = new_client()

        client.custom_request(action=Action.LOGIN, path=path).assert_not_found()

        mock.verify_auth_not_requested(client.token)
        mock.verify_do_action_not_requested(client.token)

    @allure.title('Запрос без API ключа')
    @allure.description('Тест проверяет обработку запроса без API ключа')
    def test_no_api_key_request(self, new_client, mock):
        client = new_client()

        client.request_without_api_key().assert_bad_request()

        mock.verify_auth_not_requested(client.token)

    @allure.title('Запрос с неверным API ключом')
    @allure.description('Тест проверяет обработку запроса с неверным API ключом')
    def test_wrong_api_key_request(self, new_client, mock):
        client = new_client()

        client.custom_request(action=Action.LOGIN, api_key='123456').assert_unauthorized()

        mock.verify_auth_not_requested(client.token)
