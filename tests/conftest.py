import os
import threading
import time

import pytest
import requests
import uvicorn
from requests import Session

from base.app_client import AppClient
from base.settings import Settings
from mock_external_service.app import MOCK_ADMIN_PREFIX, app as mock_app
from mock_external_service.client import MockClient, no_token


def _wait_for_mock(url: str, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            requests.get(f'{url}{MOCK_ADMIN_PREFIX}/health', timeout=0.5)
            return
        except requests.ConnectionError as exc:
            last_error = exc
            time.sleep(0.1)

    raise RuntimeError(f'mock_external_service недоступен по адресу {url}') from last_error


@pytest.fixture(scope='session')
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope='session')
def session():
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope='session', autouse=True)
def mock_server(settings):
    # Один процесс или несколько (при использовании xdist)
    worker_id = os.environ.get('PYTEST_XDIST_WORKER')
    should_start = settings.MOCK_AUTOSTART and worker_id in (None, 'gw0')

    server = None
    thread = None

    if should_start:
        config = uvicorn.Config(
            mock_app, host=settings.MOCK_HOST, port=settings.MOCK_PORT, log_level='warning'
        )
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()

    _wait_for_mock(settings.MOCK_URL)

    # Изоляция держится на привязке к token, а для тестов без токена отдельный воркер с маркировкой no_token
    if worker_id is None:
        requests.post(f'{settings.MOCK_URL}{MOCK_ADMIN_PREFIX}/reset', timeout=settings.CONNECT_TIMEOUT)

    yield

    if server is not None and thread is not None:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.fixture
def mock(settings, request) -> MockClient:
    track_tokenless = no_token.mark in request.node.iter_markers('xdist_group')
    return MockClient(settings=settings, track_tokenless=track_tokenless)


@pytest.fixture
def new_client(session, settings):
    """
    Каждый созданный клиент разлогинивается после теста.
    """
    created = []

    def _new_client(token: str | None = None) -> AppClient:
        client = AppClient(session=session, settings=settings, token=token)
        created.append(client)
        return client

    yield _new_client

    for client in created:
        client.logout()

