import os

from dotenv import load_dotenv

load_dotenv()


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


class Settings:
    SHOW_CONSOLE_LOG = _bool_env('SHOW_CONSOLE_LOG', True)
    SHOW_HEADERS = _bool_env('SHOW_HEADERS', False)
    CONNECT_TIMEOUT = 30

    def __init__(self):
        self.BASE_URL = os.getenv('BASE_URL', 'http://localhost:8080')
        self.API_KEY = os.getenv('API_KEY', '123')
        self.MOCK_HOST = os.getenv('MOCK_HOST', 'localhost')
        self.MOCK_PORT = int(os.getenv('MOCK_PORT', '8888'))
        """Поднимать ли мок в процессе тестов. False - мок уже поднят снаружи (docker)."""
        self.MOCK_AUTOSTART = _bool_env('MOCK_AUTOSTART', True)

    @property
    def MOCK_URL(self) -> str:
        return f'http://{self.MOCK_HOST}:{self.MOCK_PORT}'
