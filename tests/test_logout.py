import allure


@allure.feature('Выход, завершение сессии')
class TestLogout:
    @allure.title('Разлогин с валидным токеном')
    @allure.description('Тест проверяет возможность разлогиниться')
    def test_logout(self, new_client, mock):
        client = new_client()

        mock.stub_auth_success(client.token)

        client.login()

        client.logout().assert_success()

    @allure.title('Разлогин незалогиненного пользователя')
    @allure.description('Тест проверяет, что разлогин недоступен без предварительной авторизации')
    def test_logout_forbidden(self, new_client):
        new_client().logout().assert_forbidden()

    @allure.title('Действия недоступны после разлогина')
    @allure.description('Тест проверяет, что действия недоступны после разлогина')
    def test_no_access_after_logout(self, new_client, mock):
        client = new_client()

        mock.stub_auth_success(client.token)

        client.login()
        client.logout()

        client.action().assert_forbidden()

        mock.verify_do_action_not_requested(client.token)

    @allure.title('Логин тем же токеном после разлогина')
    @allure.description('Тест проверяет возможность разлогиниться и повторно авторизоваться с тем же токеном')
    def test_login_with_same_token_after_logout(self, new_client, mock):
        client = new_client()

        mock.stub_auth_success(client.token)

        client.login()
        client.logout()

        client.login().assert_success()

        mock.verify_auth_requested(client.token)
