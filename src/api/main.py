import uvicorn
from fastapi import FastAPI
from database.queries import Queries
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import auth

app = FastAPI()

app.include_router(auth, prefix="/auth")

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


@app.post("/receipts/")
def insert_receipt(created_at:datetime, id_employee:int):
    Queries.insert_receipt(created_at,id_employee)
    return {"message":"success"}

@app.post("/sales/")
def insert_sale(id_receipt:int, id_product:int, quintity:int):
    Queries.insert_sale(id_receipt,id_product,quintity)
    return {"message":"success"}

if __name__ == "__main__":
    uvicorn.run(app)