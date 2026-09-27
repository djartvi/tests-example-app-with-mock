import allure
import pytest
import requests

from base.settings import Settings
from mock_external_service.app import ACTION_PATH, AUTH_PATH, MOCK_ADMIN_PREFIX

# Тесты без токена - на один воркер по очереди: вызов без токена к тесту иначе не привязать.
no_token = pytest.mark.xdist_group('no_token')


class MockClient:
    """
    Стабы и верификация привязаны к token.
    """

    def __init__(self, settings: Settings, track_tokenless: bool = False):
        self.settings = settings
        self.base_url = settings.MOCK_URL
        # Журнал только дописывается: проверка без токена смотрит лишь вызовы после этой точки.
        self._tokenless_seen = (
            {path: len(self._fetch_calls(path, None)) for path in (AUTH_PATH, ACTION_PATH)}
            if track_tokenless else None
        )

    def _stub(self, path: str, status_code: int, token: str) -> None:
        response = requests.post(
            f'{self.base_url}{MOCK_ADMIN_PREFIX}/stub',
            json={'path': path, 'status_code': status_code, 'token': token},
            timeout=self.settings.CONNECT_TIMEOUT
        )
        response.raise_for_status()

    def _fetch_calls(self, path: str, token: str | None) -> list[dict]:
        params = {'path': path}
        if token:
            params['token'] = token

        response = requests.get(
            f'{self.base_url}{MOCK_ADMIN_PREFIX}/calls',
            params=params,
            timeout=self.settings.CONNECT_TIMEOUT
        )
        response.raise_for_status()
        calls = response.json()['calls']

        return calls if token else [call for call in calls if not call['token']]

    def _calls(self, path: str, token: str | None) -> list[dict]:
        if token:
            return self._fetch_calls(path, token)

        if self._tokenless_seen is None:
            raise RuntimeError('Проверка без токена работает только в тесте с @no_token')

        return self._fetch_calls(path, None)[self._tokenless_seen[path]:]

    @allure.step('Настройка заглушки для успешной авторизации')
    def stub_auth_success(self, token: str) -> None:
        self._stub(AUTH_PATH, 200, token)

    @allure.step('Настройка заглушки ошибки сервера при авторизации')
    def stub_auth_server_error(self, token: str) -> None:
        self._stub(AUTH_PATH, 500, token)

    @allure.step('Настройка заглушки для успешного запроса ACTION')
    def stub_do_action_success(self, token: str) -> None:
        self._stub(ACTION_PATH, 200, token)

    @allure.step('Настройка заглушки ошибки сервера при запросе ACTION')
    def stub_do_action_server_error(self, token: str) -> None:
        self._stub(ACTION_PATH, 500, token)

    @allure.step('Проверка, что приложение отправляет запрос авторизации')
    def verify_auth_requested(self, token: str) -> None:
        assert self._calls(AUTH_PATH, token), \
            f'Ожидали запрос {AUTH_PATH} с token={token}, но его не было'

    @allure.step('Проверка, что приложение отправляет запрос ACTION')
    def verify_do_action_requested(self, token: str) -> None:
        assert self._calls(ACTION_PATH, token), \
            f'Ожидали запрос {ACTION_PATH} с token={token}, но его не было'

    @allure.step('Проверка, что приложение не отправляет запрос авторизации')
    def verify_auth_not_requested(self, token: str | None = None) -> None:
        calls = self._calls(AUTH_PATH, token)
        assert not calls, \
            f'Не ожидали запросов {AUTH_PATH} с token={token}, получили: {calls}'

    @allure.step('Проверка, что приложение не отправляет запрос ACTION')
    def verify_do_action_not_requested(self, token: str | None = None) -> None:
        calls = self._calls(ACTION_PATH, token)
        assert not calls, \
            f'Не ожидали запросов {ACTION_PATH} с token={token}, получили: {calls}'
