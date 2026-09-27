"""
HTTP-сервер, к которому обращается тестируемое приложение (jar).
"""

import asyncio
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

AUTH_PATH = '/auth'
ACTION_PATH = '/doAction'
# Служебные эндпоинты для тестов, префикс не пересекается с путями внешнего сервиса.
MOCK_ADMIN_PREFIX = '/_mock'
UNSTUBBED_STATUS = 404

app = FastAPI(title='mock-service')

_lock = asyncio.Lock()
_default_status: dict[str, int] = {}
_token_status: dict[tuple[str, str], int] = {}
_calls: list[dict] = []


class StubRequest(BaseModel):
    path: str
    status_code: int
    token: str | None = None


def _resolve_status(path: str, token: str | None) -> int:
    if token and (path, token) in _token_status:
        return _token_status[(path, token)]
    return _default_status.get(path, UNSTUBBED_STATUS)


async def _handle_external_request(request: Request, path: str) -> JSONResponse:
    form = await request.form()
    token = form.get('token') or None

    async with _lock:
        _calls.append({
            'path': path,
            'token': token,
            'content_type': request.headers.get('content-type'),
            'body': dict(form),
            'time': time.time()
        })
        status_code = _resolve_status(path, token)

    return JSONResponse(content={}, status_code=status_code)


@app.post(AUTH_PATH)
async def auth(request: Request) -> JSONResponse:
    return await _handle_external_request(request, AUTH_PATH)


@app.post(ACTION_PATH)
async def do_action(request: Request) -> JSONResponse:
    return await _handle_external_request(request, ACTION_PATH)


@app.get(f'{MOCK_ADMIN_PREFIX}/health')
async def health() -> dict:
    return {'result': 'OK'}


@app.post(f'{MOCK_ADMIN_PREFIX}/stub')
async def stub(body: StubRequest) -> dict:
    async with _lock:
        if body.token:
            _token_status[(body.path, body.token)] = body.status_code
        else:
            _default_status[body.path] = body.status_code
    return {'result': 'OK'}


@app.post(f'{MOCK_ADMIN_PREFIX}/reset')
async def reset() -> dict:
    async with _lock:
        _default_status.clear()
        _token_status.clear()
        _calls.clear()
    return {'result': 'OK'}


@app.get(f'{MOCK_ADMIN_PREFIX}/calls')
async def calls(path: str | None = None, token: str | None = None) -> dict:
    async with _lock:
        result = list(_calls)

    if path is not None:
        result = [call for call in result if call['path'] == path]
    if token is not None:
        result = [call for call in result if call['token'] == token]

    return {'calls': result}
