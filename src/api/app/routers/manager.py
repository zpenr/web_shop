from fastapi import APIRouter, Depends, HTTPException, status
from ..db.queries import Queries
from api.app.dependencies import create_session
from sqlalchemy.orm import Session
from ..schemas.schemas import UserPublicSchema, SaleSchema
from api.app.core.security import get_permissions
from api.app.schemas import schemas

manager = APIRouter(tags=["manager"])


@manager.get("/childrens/", response_model=list[UserPublicSchema])
def get_all_childrens(boss_id: int, session: Session = Depends(create_session)):
    employees_orm = Queries.get_childrens(boss_id, session)
    employees_schema = [UserPublicSchema.model_validate(row) for row in employees_orm]
    return employees_schema


@manager.get("/sales/", response_model=list[SaleSchema])
def get_childrens_sales(boss_id: int, session: Session = Depends(create_session)):
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
    if not permissions.add_boss:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't do this",
        )
    Queries.dismiss(id, boss_id, session)
    return {"message": "success"}
