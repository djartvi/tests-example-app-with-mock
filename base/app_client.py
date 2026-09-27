from enum import StrEnum

import allure
from requests import Session

from base.base_request import BaseRequest
from base.helpers import generate_token
from base.base_response import BaseResponse
from base.settings import Settings

ENDPOINT_PATH = '/endpoint'
TOKEN_PARAM = 'token'
ACTION_PARAM = 'action'
API_KEY_HEADER = 'X-Api-Key'


class Action(StrEnum):
    LOGIN = 'LOGIN'
    ACTION = 'ACTION'
    LOGOUT = 'LOGOUT'


class AppClient(BaseRequest):
    """Клиент тестируемого приложения."""

    def __init__(self, session: Session, settings: Settings, token: str | None = None):
        super().__init__(session=session, settings=settings)
        self.token = token if token is not None else generate_token()

    def _resolve_token(self, token: str | None = None) -> str:
        return self.token if token is None else token

    def _request(self, api_key: str, token: str, action: str, path: str) -> BaseResponse:
        return self._post(
            path=path,
            headers={API_KEY_HEADER: api_key},
            form={TOKEN_PARAM: token, ACTION_PARAM: action}
        )

    @allure.step('Логин')
    def login(self, token: str | None = None) -> BaseResponse:
        return self._request(self.settings.API_KEY, self._resolve_token(token), Action.LOGIN, ENDPOINT_PATH)

    @allure.step('Действие')
    def action(self, token: str | None = None) -> BaseResponse:
        return self._request(self.settings.API_KEY, self._resolve_token(token), Action.ACTION, ENDPOINT_PATH)

    @allure.step('Завершение сессии')
    def logout(self, token: str | None = None) -> BaseResponse:
        return self._request(self.settings.API_KEY, self._resolve_token(token), Action.LOGOUT, ENDPOINT_PATH)

    @allure.step('Отправка запроса ключ={api_key}, токен={token}, действие={action}, адрес={path}')
    def custom_request(
            self,
            action: str,
            api_key: str | None = None,
            token: str | None = None,
            path: str | None = None
    ) -> BaseResponse:
        return self._request(
            api_key=self.settings.API_KEY if api_key is None else api_key,
            token=self._resolve_token(token),
            action=action,
            path=ENDPOINT_PATH if path is None else path
        )

    @allure.step('Запрос без API ключа')
    def request_without_api_key(self, action: str = Action.LOGIN) -> BaseResponse:
        return self._post(
            path=ENDPOINT_PATH,
            form={TOKEN_PARAM: self.token, ACTION_PARAM: action}
        )

    @allure.step('Запрос без параметра token')
    def request_without_token(self, action: str) -> BaseResponse:
        return self._post(
            path=ENDPOINT_PATH,
            headers={API_KEY_HEADER: self.settings.API_KEY},
            form={ACTION_PARAM: action}
        )

    @allure.step('Запрос без параметра action')
    def request_without_action(self, token: str | None = None) -> BaseResponse:
        return self._post(
            path=ENDPOINT_PATH,
            headers={API_KEY_HEADER: self.settings.API_KEY},
            form={TOKEN_PARAM: self._resolve_token(token)}
        )
