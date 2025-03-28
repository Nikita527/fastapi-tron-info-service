import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from tronpy import Tron

from app.api.pagination import (
    Page,
    paginate,
    PaginationParams,
    get_pagination_params,
)
from app.database import get_session
from app.api.endpoints.auth import get_current_user
from app.schemas.wallet import (
    WalletDataResponse,
    WalletRequest,
    WalletInfoResponse,
)
from app.models.wallet_queries import WalletQuery

router = APIRouter(tags=["Взаимодействие с кошельком"])

tron_client = Tron()


def fetch_wallet_data(wallet_address: str) -> WalletDataResponse:
    """
    Функция для получения информации о кошельке:
    - баланс TRX;
    - bandwidth;
    - energy.
    """
    try:
        # Получаем информацию о кошельке (баланс TRX)
        account_data = tron_client.get_account(wallet_address)
        trx_balance = account_data.get("balance", 0)

        # Получаем ресурсы аккаунта: bandwidth и energy
        resource_data = tron_client.get_account_resource(wallet_address)
        # Ниже использованы примерные имена ключей
        bandwidth = resource_data.get("NetLimit", 0)
        energy = resource_data.get("EnergyLimit", 0)

        return WalletInfoResponse(
            wallet_address=wallet_address,
            trx_balance=trx_balance,
            bandwidth=bandwidth,
            energy=energy,
        )
    except Exception as e:
        raise Exception(f"Ошибка при получении данных из сети Tron: {str(e)}")


@router.post(
    "/wallet-info",
    response_model=WalletInfoResponse,
    dependencies=[Depends(get_current_user)],
)
async def get_wallet_info(
    data: WalletRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Эндпоинт для получения информации по кошельку:
    - Запрашивает данные о балансе, bandwidth и energy у сети Tron;
    - Логирует запрос в БД.
    """
    try:
        # Выполняем блокирующую функцию в отдельном потоке,
        # чтобы не блокировать event loop
        wallet_data = await asyncio.to_thread(
            fetch_wallet_data, data.wallet_address
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Логирование запроса в базе данных
    new_query = WalletQuery(
        wallet_address=data.wallet_address, created_at=datetime.now()
    )
    session.add(new_query)
    await session.commit()

    return wallet_data


@router.get(
    "/queries",
    response_model=Page[WalletDataResponse],
    dependencies=[Depends(get_current_user)],
)
async def get_queries(
    session: AsyncSession = Depends(get_session),
    pagination: PaginationParams = Depends(get_pagination_params),
):
    """
    Эндпоинт для получения списка последних запросов (с пагинацией):
      - page – номер страницы,
      - size – сколько записей на странице.
    """
    result = await session.execute(
        select(WalletQuery).order_by(WalletQuery.created_at.desc())
    )
    queries = result.scalars().all()
    mapped_queries = [
        WalletDataResponse(
            wallet_address=query.wallet_address, created_at=query.created_at
        )
        for query in queries
    ]
    return paginate(mapped_queries, pagination)
