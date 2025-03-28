import pytest_asyncio
import pytest
from typing import AsyncGenerator
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from app.models.base import Base
from app.models.wallet_queries import WalletQuery

# Используем in-memory базу данных для юнит-тестов
DATABASE_URL_UNIT = "sqlite+aiosqlite:///:memory:"

engine_unit = create_async_engine(DATABASE_URL_UNIT, echo=True)
TestSessionLocal = sessionmaker(
    engine_unit, class_=AsyncSession, expire_on_commit=False
)


# Фикстура для подготовки базы данных (создает и удаляет таблицы)
@pytest_asyncio.fixture(scope="module", autouse=True)
async def prepare_db():
    # Создаем таблицы перед прохождением тестов
    async with engine_unit.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Удаляем таблицы после тестов
    async with engine_unit.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest.mark.asyncio()
async def test_wallet_query_insert(session: AsyncSession):
    """
    Юнит-тест:
    - Создаем новый объект WalletQuery,
    - Добавляем его в сессию и вызываем commit,
    - Затем выбираем запись из БД и проверяем корректность.
    """
    new_wallet_address = "T987654321"
    new_query = WalletQuery(
        wallet_address=new_wallet_address, created_at=datetime.now()
    )
    session.add(new_query)
    await session.commit()

    # Выполняем выборку из базы
    result = await session.execute(
        select(WalletQuery).filter_by(wallet_address=new_wallet_address)
    )
    query_obj = result.scalars().first()

    assert query_obj is not None
    assert query_obj.wallet_address == new_wallet_address
