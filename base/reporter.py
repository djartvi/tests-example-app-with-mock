import allure
from requests import Response
from requests_toolbelt.utils import dump


class Reporter:
    """Вложения в Allure."""

    @staticmethod
    def attach(response: Response) -> None:
        request = response.request
        allure.attach(
            dump.dump_all(response).decode('utf-8', errors='replace'),
            name=f'{request.method} {request.path_url} -> {response.status_code}',
            attachment_type=allure.attachment_type.TEXT
        )
