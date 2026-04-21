import uvicorn
from fastapi import FastAPI
from database.queries import Queries
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import auth
from routers.manager import manager
from typing import Optional

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
def insert_product(name:str, price: int, id_category:int, quantity_at_storage:int) -> dict:
    Queries.insert_product(name,price,id_category,quantity_at_storage)
    return {"message":"success"}

@app.post("/categories/")
def insert_category(name:str) -> dict:
    Queries.insert_category(name)
    return{"message":"success"}

@app.get("/products/")
def all_products():
    res = Queries.all_products()
    return res

@app.post("/jobs/")
def insert_job(name: str, roots:int):
    Queries.insert_job(name,roots)
    return {"message":"success"}

@app.post("/sales/")
def insert_sale(created_at:datetime, id_employee:int, id_product:int, quintity:int):
    if Queries.insert_sale(created_at, id_employee, id_product, quintity):
        return {"message":"success"}
    return {"message":"Something went wrong"}

@app.get("/categories/")
def all_categories():
    return Queries.all_categories()

@app.get("/jobs/")
def all_jobs():
    return Queries.all_jobs()

@app.get("/receipts/")
def all_receipts():
    return Queries.all_receipts()

@app.get("/employees/")
def all_employees():
    return Queries.all_employees()

@app.get("/sales/")
def all_sales():
    return Queries.all_sales()

@app.patch("/employees/")
def add_boss(id:int,boss_id:int):
    return Queries.add_boss(id,boss_id)

@app.patch("/products/")
def update_product(
    product_id:int,
    price: Optional[int] = None,
    quantity_at_storage: Optional[int] = None
    ):
    Queries.update_product(product_id,price,quantity_at_storage)
    return {"massege":"success"}

@app.delete("/products/")
def delete_product(id:int):
    Queries.delete_product(id)
    return {"massege":"success"}

@app.get("/products/{id}")
def product_by_id(id:int):
    return Queries.get_product_by_id(id)

@app.get("/products/filter/")
def filtered_products(category_id:int|None, min_price: float = 0, max_price:float = 10**8):
    return Queries.filtered_products(category_id, min_price, max_price)

@app.get("/products/category/")
def products_by_category(category_id:int):
    return Queries.products_by_category(category_id)

@app.get("/employee/{id}/sales")
def employee_sales(id:int):
    return Queries.employee_sales(id)

if __name__ == "__main__":
    uvicorn.run(app)