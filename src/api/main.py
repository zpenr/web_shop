import uvicorn
from fastapi import FastAPI
from database.queries import Queries
from datetime import datetime
app = FastAPI()

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
def insert_job(name: str):
    Queries.insert_job(name)
    return {"message":"success"}

@app.post("/employees/")
def insert_employee(name:str, surname:str, login:str, password:str, id_job):
    Queries.insert_employee(name,surname,login,password,id_job)
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