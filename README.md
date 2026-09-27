# Тестирование REST API приложения

Автотесты для веб-сервиса, проверяющие работу эндпоинта аутентификации и действий
пользователя. Python-аналог Java-проекта `NC_Java_App_Test` (покрытие jar приложения тестами по ТЗ).

**Технологический стек:** Python 3.12, pytest, pytest-xdist, requests, FastAPI + uvicorn
(вместо WireMock), Allure, Docker Compose.

## Контракт тестируемого приложения

Приложение (jar) принимает запросы:

```
POST /endpoint
Content-Type: application/x-www-form-urlencoded
X-Api-Key: <api_key>

token=<32 символа из A-Z0-9>&action=LOGIN|ACTION|LOGOUT
```

и отвечает JSON `{"result": "OK"|"ERROR", "message": "..."}` с кодами:

- `200` — успех;
- `400` — невалидный запрос (нет `token`/`action`, неверный формат токена, неизвестный `action`);
- `401` — неверный `X-Api-Key`;
- `403` — действие недоступно (нет активной сессии для `ACTION`/`LOGOUT`);
- `404` — неверный адрес;
- `>499` — ошибка при обращении к внешнему сервису.

Само приложение при `LOGIN`/`ACTION` ходит на внешний сервис (`POST /auth`, `POST /doAction`),
пробрасывая туда `token` в теле запроса. Подмена внешнего сервиса - пакет `mock_external_service/`.

## ОГРАНИЧЕНИЕ: jar в репозитории нет

Чтобы набор можно было прогнать зелёным и без jar, в репозитории есть `mock_app/` —
мок приложения, реализующий тот же контракт (парный к `mock_external_service/`, который подменяет
внешний сервис). Как подставить настоящий jar — см. `app/README.md`.

## Структура проекта

```
base/
  base_request.py             # BaseRequest: транспорт (таймаут, логирование), возвращает BaseResponse
  app_client.py               # AppClient(BaseRequest): методы API + Action и константы контракта
  base_response.py            # BaseResponse: именованные ассерты (assert_success, assert_forbidden, ...)
  settings.py                 # Settings из переменных окружения
  logger.py                   # лог запросов/ответов в консоль
  helpers.py                  # generate_token
mock_external_service/app.py  # мок внешнего сервиса (замена WireMock) + MockClient (заглушки, верификация)
mock_app/app.py               # мок приложения: контракт без jar, чтобы прогнать набор зелёным
tests/                        # тесты (по файлам) + conftest.py с фикстурами
docker/                       # docker-compose.yml (по умолчанию) и docker-compose.app.yml (реальный jar)
app/                          # слот для реального jar (app.jar) + инструкция
```

## Быстрый старт (локально)

```bash
source .venv/bin/activate
pip install -r requirements.txt

python -m mock_app.app &            # мок приложения на 8080 (или свой jar, см. app/README.md)

pytest                              # мок внешнего сервиса поднимается сам (MOCK_AUTOSTART=true)
pytest -n auto                      # параллельно через xdist
pytest --alluredir=allure-results   # без этого флага результатов собрано не будет
allure serve allure-results         # нужен Allure CLI; каталог указывать явно
```

Переменные окружения — см. `.env.example` (скопировать в `.env`, подхватывается автоматически).
Подробный лог запросов/ответов в консоль включается `SHOW_CONSOLE_LOG`, лог заголовков — `SHOW_HEADERS`.

## Docker

```bash
# mock-service + mock-app + tests: всё зелёное без jar
docker compose -f docker/docker-compose.yml up --build

# с настоящим jar (см. app/README.md): BASE_URL переключается на сервис app
docker compose -f docker/docker-compose.yml -f docker/docker-compose.app.yml up
```

## Архитектурные решения

**Мок** - свой сервис на FastAPI `mock_external_service/app.py` поднимается через uvicorn.

**Запрос и ответ — вложением на шаг, а не простынёй stdout.** allure-pytest по умолчанию
цепляет к тесту весь перехваченный stdout: один блоб на тест вместо привязки к шагу, с
ANSI-кодами внутри и с исчезновением при `pytest -s`. Он отключён флагом
`--allure-no-capture` в `pytest.ini`, а `base/reporter.py::Reporter.attach` кладёт к
текущему шагу дамп запроса и ответа (`requests_toolbelt.utils.dump.dump_all`). Полный
запрос/ответ по-прежнему пишется в консоль (`base/logger.py`) под флагами
`SHOW_CONSOLE_LOG`/`SHOW_HEADERS`.
