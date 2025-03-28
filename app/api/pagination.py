from math import ceil
from typing import Generic, List, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Параметры пагинации.
    По умолчанию: page=1, size=10.
    """

    page: int = 1
    size: int = 10

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.size


def get_pagination_params(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(
        10, ge=1, le=100, description="Количество записей на странице"
    ),
) -> PaginationParams:
    """
    Зависимость для получения параметров пагинации из строки запроса.
    """
    return PaginationParams(page=page, size=size)


class Page(BaseModel, Generic[T]):
    """
    Генерик-модель ответа пагинации.
    Теперь наследуется от BaseModel, что соответствует Pydantic v2.

    Содержит:
      • items — список объектов на текущей странице,
      • total — общее число объектов,
      • page — номер текущей страницы,
      • size — количество объектов на странице,
      • total_pages — общее число страниц.
    """

    items: List[T]
    total: int
    page: int
    size: int
    total_pages: int

    @classmethod
    def create(
        cls, items: List[T], total: int, page: int, size: int
    ) -> "Page[T]":
        total_pages = ceil(total / size) if size > 0 else 1
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )


def paginate(data: List[T], pagination: PaginationParams = None) -> Page[T]:
    """
    Функция для разделения полного списка данных на страницы.

    Принимает:
      • data — полный список объектов,
      • pagination — объект параметров пагинации (если не передан, будут использованы значения по умолчанию).  # noqa: E501

    Возвращает объект Page с обрезанным набором данных и метаданными.
    """
    if pagination is None:
        pagination = PaginationParams()
    total = len(data)
    start = pagination.skip
    end = start + pagination.size
    items = data[start:end]
    return Page.create(items, total, pagination.page, pagination.size)


def add_pagination(app):
    """
    Функция для обратной совместимости.
    Если в вашем main.py вызывается add_pagination(app),
    можно оставить этот вызов — он ничего не настраивает,
    но обеспечивает одинаковый интерфейс, как в fastapi-pagination.
    """
    return app
