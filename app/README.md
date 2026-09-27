# Тестируемое приложение

В этом репозитории нет реального jar тестируемого сервиса (он ещё в разработке, тесты пишем без него).

Здесь два варианта того, что присваиваетсяд `BASE_URL`:

## 1. `mock_app/` — мок приложения (по умолчанию)

Реализация контракта из корневого README.md на FastAPI, лежит в пакете `mock_app/` рядом
с `mock_external_service/`. Нужен, чтобы фреймворк можно было прогнать зелёным без jar и убедиться,
что тесты, заглушки и верификация работают. Намеренно не импортирует ничего из `base/`
и `mock_external_service/` — иначе тесты частично проверяли бы сами себя через общий код.

```bash
python -m mock_app.app     # слушает 8080, ходит на mock_external_service по MOCK_URL
pytest                     # в другом терминале
```

Переменные окружения (аналоги `-Dsecret` / `-Dmock` у настоящего jar):
`API_KEY` (по умолчанию `123`), `MOCK_URL` (`http://localhost:8888`), `PORT` (`8080`).

## 2. Настоящий jar

1. Положить jar сюда под именем `app.jar`:
   `cp /path/to/internal-0.0.1-SNAPSHOT.jar app/app.jar`
2. Запустить:
   ```bash
   docker compose -f docker/docker-compose.yml -f docker/docker-compose.app.yml up
   ```
   `BASE_URL` переключится на сервис `app`. Контейнер `mock-app` тоже поднимется, но
   простаивает — тесты в него не ходят.

   Своего `Dockerfile` для jar в репозитории нет: сервис `app` берёт готовый образ
   `eclipse-temurin:17-jre` (Java 17, только рантайм; версия — из `maven.compiler.target`
   исходного Java-проекта), а каталог `app/` монтируется в него как `/app`. Java на
   машине ставить не нужно, пересобирать нечего.

Локально без Docker:

```bash
java -jar -Dsecret=<API_KEY> -Dmock=http://<MOCK_HOST>:<MOCK_PORT>/ app.jar
```

и указать те же значения в `.env` (`BASE_URL`, `API_KEY`, `MOCK_HOST`, `MOCK_PORT`).
