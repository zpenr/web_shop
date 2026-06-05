from fastapi import APIRouter, Depends
from api.app.db.queries import Queries
from api.app.dependencies import create_session
from sqlalchemy.orm import Session
from api.app.schemas.schemas import UserPublicSchema, SaleSchema
from api.app.core.security import get_permissions
from api.app.schemas import schemas

manager = APIRouter(tags=["manager"])


@manager.get("/childrens/", response_model=list[UserPublicSchema])
def get_all_childrens(boss_id: int, session: Session = Depends(create_session)):
    """Возвращает список всех подчинённых сотрудников для указанного руководителя.

    Args:
        boss_id: Идентификатор руководителя (начальника).
        session: Сессия SQLAlchemy, внедряемая зависимостью.

    Returns:
        list[UserPublicSchema]: Список подчинённых сотрудников (публичные данные).
    """
    employees_orm = Queries.get_childrens(boss_id, session)
    employees_schema = [UserPublicSchema.model_validate(row) for row in employees_orm]
    return employees_schema


@manager.get("/sales/", response_model=list[SaleSchema])
def get_childrens_sales(boss_id: int, session: Session = Depends(create_session)):
    """Возвращает все продажи, совершённые подчинёнными сотрудниками руководителя.

    Args:
        boss_id: Идентификатор руководителя.
        session: Сессия SQLAlchemy.

    Returns:
        list[SaleSchema]: Список продаж, совершённых подчинёнными.
    """
    sales_orm = Queries.get_childrens_sales(boss_id, session)
    sales_schema = [SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema


@manager.delete("/childrens/")
def dismiss_employee(
    id: int,
    boss_id: int,
    session: Session = Depends(create_session),
    permissions: schemas.PermissionSchema = Depends(get_permissions),
):
    """Увольняет подчинённого сотрудника.

    Args:
        id: Идентификатор увольняемого сотрудника.
        boss_id: Идентификатор текущего руководителя (нужен для проверки подчинённости).
        session: Сессия SQLAlchemy.
        permissions: Права доступа текущего пользователя (должны включать право на увольнение).

    Returns:
        dict: Сообщение об успешном увольнении {"message": "success"}.
    """
    Queries.dismiss(id, boss_id, session)
    return {"message": "success"}
