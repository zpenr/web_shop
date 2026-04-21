import uvicorn
from fastapi import FastAPI, Depends,HTTPException,status
from database.queries import Queries
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import auth
from routers.manager import manager
from typing import Optional
from database.setup import create_session
from sqlalchemy.orm import Session

app = FastAPI()

app.include_router(auth, prefix="/auth")
app.include_router(manager, prefix="/manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/products/')
def insert_product(name:str, price: int, id_category:int, quantity_at_storage:int, session: Session = Depends(create_session)) -> dict:
    Queries.insert_product(name,price,id_category,quantity_at_storage,session)
    return {"message":"success"}

@app.post("/categories/")
def insert_category(name:str, session: Session = Depends(create_session)) -> dict:
    Queries.insert_category(name,session)
    return{"message":"success"}

@app.get("/products/")
def all_products(session: Session = Depends(create_session)):
    res = Queries.all_products(session)
    return res

@app.post("/jobs/")
def insert_job(name: str, roots:int, session: Session = Depends(create_session)):
    Queries.insert_job(name,roots,session)
    return {"message":"success"}

@app.post("/sales/")
def insert_sale(created_at:datetime, id_employee:int, id_product:int, quintity:int, session: Session = Depends(create_session)):
    try:
        Queries.insert_sale_with_storage_check(created_at,id_employee,id_product,quintity,session)
        return {"message":"success"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Something went wrong")

@app.get("/categories/")
def all_categories(session: Session = Depends(create_session)):
    return Queries.all_categories(session)

@app.get("/jobs/")
def all_jobs(session: Session = Depends(create_session)):
    return Queries.all_jobs(session)

@app.get("/receipts/")
def all_receipts(session: Session = Depends(create_session)):
    return Queries.all_receipts(session)

@app.get("/employees/")
def all_employees(session: Session = Depends(create_session)):
    return Queries.all_employees(session)

@app.get("/sales/")
def all_sales(session: Session = Depends(create_session)):
    return Queries.all_sales(session)

@app.patch("/employees/")
def add_boss(id:int,boss_id:int, session: Session = Depends(create_session)):
    return Queries.add_boss(id,boss_id,session)

@app.patch("/products/")
def update_product(
    product_id:int,
    price: Optional[int] = None,
    quantity_at_storage: Optional[int] = None,
    session: Session = Depends(create_session)
    ):
    Queries.update_product(product_id,price,quantity_at_storage,session)
    return {"massege":"success"}

@app.delete("/products/")
def delete_product(id:int, session: Session = Depends(create_session)):
    Queries.delete_product(id,session)
    return {"massege":"success"}

@app.get("/products/{id}")
def product_by_id(id:int, session: Session = Depends(create_session)):
    return Queries.get_product_by_id(id,session)

@app.get("/products/filter/")
def filtered_products(category_id:int|None, min_price: float = 0, max_price:float = 10**8, session: Session = Depends(create_session)):
    return Queries.filtered_products(category_id, min_price, max_price,session)

@app.get("/products/category/")
def products_by_category(category_id:int, session: Session = Depends(create_session)):
    return Queries.products_by_category(category_id,session)

@app.get("/employee/{id}/sales")
def employee_sales(id:int, session: Session = Depends(create_session)):
    return Queries.employee_sales(id,session)

if __name__ == "__main__":
    uvicorn.run(app)