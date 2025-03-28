import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.base import Base
from app.models.users import User
from app.database import get_session
from app.api.endpoints.auth import get_current_user

# Для тестов определяем in-memory базу данных
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


# Переопределяем зависимость get_session для использования тестовой БД
async def override_get_session():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


async def override_get_current_user():
    user = User()
    user.id = 1
    user.email = "test@test.com"
    user.hashed_password = "fake"
    return user


app.dependency_overrides[get_current_user] = override_get_current_user


# Создаем клиента для тестирования
@pytest.fixture(scope="module")
def client():
    # Перед запуском тестов создадим таблицы в in-memory БД
    import asyncio

    async def init_models():
        async with engine_test.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_models())

    with TestClient(app) as c:
        yield c


def test_wallet_info_endpoint(client, monkeypatch):
    """
    Интеграционный тест эндпоинта POST /wallet-info:
      - переопределение fetch_wallet_data, чтобы не обращаться к сети Tron;
      - отправка запроса и проверка наличия нужных ключей в ответе;
      - запись запроса в БД (проверку этого можно провести в отдельном тесте).
    """
    # Замокаем функцию, которая получает данные из Tron
    from app.api.endpoints import wallet

    def mock_fetch_wallet_data(wallet_address: str):
        # Возвращаем предопределённые данные
        from app.schemas.wallet import WalletInfoResponse

        return WalletInfoResponse(
            wallet_address=wallet_address,
            trx_balance=1000,
            bandwidth=200,
            energy=300,
        )

    monkeypatch.setattr(wallet, "fetch_wallet_data", mock_fetch_wallet_data)

    payload = {"wallet_address": "T123456789"}
    response = client.post("/api/wallet-info", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["wallet_address"] == "T123456789"
    assert data["trx_balance"] == 1000
    assert data["bandwidth"] == 200
    assert data["energy"] == 300


def test_queries_endpoint(client):
    """
    Интеграционный тест эндпоинта GET /queries. Этот запрос
    возвращает список логов запросов с пагинацией.
    """
    response = client.get("/api/queries?page=1&size=10")
    assert response.status_code == 200, response.text
    data = response.json()
    # Проверяем базовую структуру пагинации
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "total_pages" in data
