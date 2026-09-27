"""
Мок тестируемого приложения, чтобы тестовый фреймворк можно было прогнать без реального jar.

Запуск:
    python -m mock_app.app                            # слушает PORT (по умолчанию 8080)
    uvicorn mock_app.app:app --port 8080              # то же через uvicorn

Переменные окружения (аналоги -Dsecret / -Dmock у настоящего jar):
    API_KEY   - X-Api-Key (по умолчанию 123)
    MOCK_URL  - адрес внешнего сервиса (по умолчанию http://localhost:8888)
    PORT      - порт приложения mock_app (по умолчанию 8080)
"""

import os
import re
import threading

import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

API_KEY = os.getenv('API_KEY', '123')
MOCK_URL = os.getenv('MOCK_URL', 'http://localhost:8888')
PORT = int(os.getenv('PORT', '8080'))

TOKEN_PATTERN = re.compile(r'^[A-Z0-9]{32}$')
ACTIONS = ('LOGIN', 'ACTION', 'LOGOUT')
UPSTREAM_TIMEOUT = 10

app = FastAPI(title='mock-app')

# Активные сессии: приложение хранит их в памяти, ключ - token.
_sessions: set[str] = set()
_lock = threading.Lock()


def ok() -> JSONResponse:
    return JSONResponse({'result': 'OK', 'message': 'done'}, status_code=200)


def error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse({'result': 'ERROR', 'message': message}, status_code=status_code)


def call_upstream(path: str, token: str) -> int:
    """Запрос во внешний сервис - mock_external_service."""
    try:
        response = requests.post(f'{MOCK_URL}{path}', data={'token': token}, timeout=UPSTREAM_TIMEOUT)
        return response.status_code
    except requests.RequestException:
        return 503


@app.post('/endpoint')
async def endpoint(request: Request):
    api_key = request.headers.get('X-Api-Key')
    if api_key is None:
        return error(400, 'no api key')
    if api_key != API_KEY:
        return error(401, 'wrong api key')

    form = await request.form()
    token = form.get('token')
    action = form.get('action')

    if token is None:
        return error(400, 'no token parameter')
    if action is None:
        return error(400, 'no action parameter')
    if not TOKEN_PATTERN.match(token):
        return error(400, 'invalid token')
    if action not in ACTIONS:
        return error(400, 'unknown action')

    if action == 'LOGIN':
        if call_upstream('/auth', token) >= 500:
            return error(500, 'upstream error')
        with _lock:
            _sessions.add(token)
        return ok()

    # ACTION и LOGOUT доступны только при активной сессии.
    with _lock:
        logged_in = token in _sessions
    if not logged_in:
        return error(403, 'not logged in')

    if action == 'ACTION':
        if call_upstream('/doAction', token) >= 500:
            return error(500, 'upstream error')
        return ok()

    with _lock:
        _sessions.discard(token)
    return ok()


@app.api_route('/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
async def not_found(path: str):
    return error(404, 'not found')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=PORT, log_level='warning')
