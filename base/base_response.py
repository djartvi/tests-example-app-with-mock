import allure
from requests import Response


class BaseResponse:
    def __init__(self, response: Response):
        self.response = response

    @property
    def status_code(self) -> int:
        return self.response.status_code

    def _assert_status_code(self, expected: int) -> None:
        assert self.status_code == expected, (
            f'Ожидали статус {expected}, получили {self.status_code}. '
            f'Тело ответа: {self.response.text}'
        )

    def assert_error_body(self) -> None:
        try:
            body = self.response.json()
        except ValueError:
            raise AssertionError(f'Ожидали JSON в теле ответа, получили: {self.response.text}')

        assert body.get('result') == 'ERROR', f'Ожидали result=ERROR, получили: {body}'
        assert isinstance(body.get('message'), str), f'Ожидали строку в message, получили: {body}'

    @allure.step('Проверка, что ответ успешен')
    def assert_success(self) -> None:
        self._assert_status_code(200)

        body = self.response.json()
        assert body.get('result') == 'OK', f'Ожидали result=OK, получили: {body}'

    @allure.step('Проверка ответа на невалидный запрос')
    def assert_bad_request(self) -> None:
        self._assert_status_code(400)
        self.assert_error_body()

    @allure.step('Проверка ответа на неверные учётные данные')
    def assert_unauthorized(self) -> None:
        self._assert_status_code(401)
        self.assert_error_body()

    @allure.step('Проверка ответа на запрос неавторизованного пользователя')
    def assert_forbidden(self) -> None:
        self._assert_status_code(403)
        self.assert_error_body()

    @allure.step('Проверка ответа на запрос по несуществующему адресу')
    def assert_not_found(self) -> None:
        self._assert_status_code(404)
        self.assert_error_body()

    @allure.step('Проверка ответа при ошибке сервера')
    def assert_server_error(self) -> None:
        assert self.status_code >= 500, (
            f'Ожидали статус 5**, получили {self.status_code}. '
            f'Тело ответа: {self.response.text}'
        )
        self.assert_error_body()
