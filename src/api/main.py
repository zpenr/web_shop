import uvicorn
from fastapi import FastAPI
from database.queries import Queries

app = FastAPI()

@app.post('/products/')
def insert_product(name:str, price: int, id_category:int, quantity_at_storage:int) -> dict:
    Queries.insert_product(name,price,id_category,quantity_at_storage)
    return {"message":"success"}

@app.post("/categories/")
def insert_category(name:str) -> dict:
    Queries.insert_category(name)
    return{"message":"success"}

if __name__ == "__main__":
    uvicorn.run(app)