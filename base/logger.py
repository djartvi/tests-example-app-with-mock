import requests

from base.settings import Settings


class Logger:
    @staticmethod
    def log_request(url, headers, body=None):
        if not Settings.SHOW_CONSOLE_LOG:
            return

        print(f'\n\033[92mЗапрос: {url}\033[0m')

        if Settings.SHOW_HEADERS:
            print(f'\033[92mЗаголовки запроса: {headers}\033[0m')

        if body is not None:
            print(f'\033[92mТело запроса: {body}\033[0m')

    @staticmethod
    def log_response(response):
        if not Settings.SHOW_CONSOLE_LOG:
            return

        print(f'\033[93mСтатус код: {response.status_code}\033[0m')

        if Settings.SHOW_HEADERS:
            print(f'\033[93mЗаголовки ответа: {response.headers}\033[0m')

        if not (response.content and response.content.strip()):
            print('\033[90mОтвет пустой\033[0m')
            return

        try:
            body = response.json()
        except (requests.exceptions.JSONDecodeError, ValueError):
            body = response.text.strip()

        print(f'\033[93mТело ответа: {body}\033[0m')
