from fastapi import APIRouter, Depends
from database.queries import Queries
from database.setup import create_session
from sqlalchemy.orm import Session
manager = APIRouter(tags=["manager"])

@manager.get("/childrens/")
def get_all_childrens(id:int, session: Session = Depends(create_session)):
    return Queries.get_childrens(id,session)

@manager.get("/sales/")
def get_childrens_sales(boss_id:int, session: Session = Depends(create_session)):
    return Queries.get_childrens_sales(boss_id,session)

@manager.delete("/childrens/")
def dismiss_employee(id:int, boss_id:int, session: Session = Depends(create_session)):
    Queries.dismiss(id,boss_id,session)
    return {"massege":"success"}