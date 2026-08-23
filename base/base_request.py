from requests import Session

from base.logger import Logger
from base.response import ApiResponse
from base.settings import Settings


class Request:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def _post(self, path: str, form: dict, headers: dict | None = None) -> ApiResponse:
        url = f'{self.settings.BASE_URL}{path}'
        headers = {
            'Accept': 'application/json',
            **(headers or {})
        }
        data = {key: str(value) for key, value in form.items()}

        Logger.log_request(url=f'POST {url}', headers=headers, body=data)

        response = self.session.post(
            url,
            headers=headers,
            data=data,
            timeout=self.settings.CONNECT_TIMEOUT
        )
        Logger.log_response(response)

        return ApiResponse(response)
