# fastapi-tron-info-service
Microservice for get information from tron

## О проекте

Данный микросервис реализует два основных эндпоинта:

- **POST /api/wallet-info**  
  Принимает адрес кошелька на блокчейне Tron, возвращает информацию о балансе TRX, bandwidth и energy, полученную с помощью библиотеки `tronpy`. При этом каждый запрос логируется в базу данных (адрес и время запроса).

- **GET /api/queries**  
  Возвращает список последних запросов с пагинацией, что позволяет отслеживать историю обращений.

Также реализованы юнит и интеграционные тесты с использованием `pytest`.

Для авторизации используется JWT, а эндпоинты аутентификации расположены в модуле `/api/auth`.


## Технологии

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [alembic](https://alembic.sqlalchemy.org/en/latest/)
- [uvicorn](https://www.starlette.io/)
- [pytest](https://docs.pytest.org/en/latest/)
- [tronpy](https://github.com/tronprotocol/tronpy)
- [Docker](https://www.docker.com/)


## Запуск проекта
Запуск натсроен через docker-compose и с помощью Makefile

- Клонируйте репозиторий

- Запустите `make start` (если установлен make)

- Если не установлен make, запустите `docker-compose -f infra/dev/docker-compose.dev.yaml up -d --build`

- Переходите на http://localhost:8000/docs

## Запуск тестов

- Создать виртуальное окружение
- Активировать виртуальное окружение
- Установить зависимости `pip install -r requirements/dev.txt`
- Запустить тесты `pytest`
