from fastapi import APIRouter
from database.queries import Queries

manager = APIRouter(tags=["manager"])

@manager.get("/childrens/")
def get_all_childrens(id:int):
    return Queries.get_childrens(id)

@manager.get("/sales/")
def get_childrens_sales(boss_id:int):
    return Queries.get_childrens_sales(boss_id)

@manager.delete("/childrens/")
def dismiss_employee(id:int, boss_id:int):
    Queries.dismiss(id,boss_id)
    return {"massege":"success"}