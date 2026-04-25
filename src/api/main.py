import uvicorn
import schemas
from fastapi import FastAPI, Depends,HTTPException,status
from database.queries import Queries
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import auth
from routers.manager import manager
from typing import Optional
from database.setup import create_session
from sqlalchemy.orm import Session
from routers.auth import get_current_user
from database.models import Employees

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

@app.get("/products/",response_model=list[schemas.ProductSchema])
def all_products(session: Session = Depends(create_session)):
    products_orm = Queries.all_products(session)
    products_schema = [schemas.ProductSchema.model_validate(row) for row in products_orm]
    return products_schema

@app.post("/jobs/")
def insert_job(name: str, roots:int, session: Session = Depends(create_session)):
    Queries.insert_job(name,roots,session)
    return {"message":"success"}

@app.post("/sales/")
def insert_sale(
    created_at: datetime, 
    id_product: int, 
    quintity: int, 
    session: Session = Depends(create_session),
    current_user: Employees = Depends(get_current_user)):
    try:
        Queries.insert_sale_with_storage_check(created_at,current_user.id,id_product,quintity,session)
        return {"message":"success"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Something went wrong")

@app.get("/categories/",response_model=list[schemas.CategorySchema])
def all_categories(session: Session = Depends(create_session)):
    categories_orm = Queries.all_categories(session)
    categories_schema = [schemas.CategorySchema.model_validate(row) for row in categories_orm]
    return categories_schema

@app.get("/jobs/",response_model=list[schemas.JobSchema])
def all_jobs(session: Session = Depends(create_session)):
    jobs_orm = Queries.all_jobs(session)
    jobs_schema = [schemas.JobSchema.model_validate(row) for row in jobs_orm]
    return jobs_schema

@app.get("/receipts/",response_model=list[schemas.ReceiptSchema])
def all_receipts(session: Session = Depends(create_session)):
    receipts_orm = Queries.all_receipts(session)
    receipts_schema = [schemas.ReceiptSchema.model_validate(row) for row in receipts_orm]
    return receipts_schema

@app.get("/employees/", response_model=list[schemas.UserPublicSchema])
def all_employees(session: Session = Depends(create_session)):
    employees_orm = Queries.all_employees(session)
    employees_schema = [schemas.UserPublicSchema.model_validate(row) for row in employees_orm]
    return employees_schema

@app.get("/sales/",response_model=list[schemas.SaleSchema])
def all_sales(session: Session = Depends(create_session)):
    sales_orm = Queries.all_sales(session)
    sales_schema = [schemas.SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema

@app.patch("/employees/")
def add_boss(id:int,boss_id:int, session: Session = Depends(create_session)):
    Queries.add_boss(id,boss_id,session)
    return {"message":"success"}

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

@app.get("/products/{id}", response_model=schemas.ProductSchema)
def product_by_id(id:int, session: Session = Depends(create_session)):
    return Queries.get_product_by_id(id,session)

@app.get("/products/filter/", response_model=list[schemas.ProductSchema])
def filtered_products(category_id:int|None, min_price: float = 0, max_price:float = 10**8, session: Session = Depends(create_session)):
    products_orm = Queries.filtered_products(category_id, min_price, max_price,session)
    products_schema = [schemas.ProductSchema.model_validate(row) for row in products_orm]
    return products_schema

@app.get("/products/category/", response_model=list[schemas.ProductSchema])
def products_by_category(category_id:int, session: Session = Depends(create_session)):
    products_orm = Queries.products_by_category(category_id,session)
    products_schema = [schemas.ProductSchema.model_validate(row) for row in products_orm]
    return products_schema

@app.get("/employee/{id}/sales", response_model=list[schemas.SaleSchema])
def employee_sales(id:int, session: Session = Depends(create_session)):
    sales_orm = Queries.employee_sales(id,session)
    sales_schema = [schemas.SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema

@app.get("/sales/filter/", response_model=list[schemas.SaleSchema])
def sales_products(min_sum: int | None = None,
            max_sum: int | None = None,
            min_date: datetime | None = None,
            max_date: datetime | None = None,
            product_id: int | None = None,
            employee_id: int | None = None, 
            session: Session = Depends(create_session)):
    
    sales_orm = Queries.filtered_sales(session,min_sum,max_sum,min_date,max_date,product_id, employee_id)
    sales_schema = [schemas.SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema

if __name__ == "__main__":
    uvicorn.run(app)