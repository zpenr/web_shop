from fastapi import APIRouter, Depends, HTTPException,status
from api.app.schemas import schemas
from api.app.db.queries import Queries
from datetime import datetime
from typing import Optional
from api.app.dependencies import create_session
from sqlalchemy.orm import Session
from api.app.routers.auth import get_current_user
from api.app.core.security import get_roots

sales = APIRouter(tags=["sales"])

@sales.post('/products/')
def insert_product(name:str, price: int, id_category:int, quantity_at_storage:int, session: Session = Depends(create_session), roots: schemas.RootSchema = Depends(get_roots)) -> dict:
    if roots.add_products:
        Queries.insert_product(name,price,id_category,quantity_at_storage,session)
        return {"message":"success"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")

@sales.post("/categories/")
def insert_category(name:str, session: Session = Depends(create_session), roots: schemas.RootSchema = Depends(get_roots)) -> dict:
    if roots.add_categories:
        Queries.insert_category(name,session)
        return{"message":"success"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")

@sales.get("/products/",response_model=list[schemas.ProductSchema])
def all_products(session: Session = Depends(create_session)):
    products_orm = Queries.all_products(session)
    products_schema = [schemas.ProductSchema.model_validate(row) for row in products_orm]
    return products_schema

@sales.post("/jobs/", response_model=schemas.JobSchema)
def insert_job(name: str, root_id:int, session: Session = Depends(create_session)):
    job_orm = Queries.insert_job(name,root_id,session)
    job_schema = schemas.JobSchema.model_validate(job_orm)
    return job_schema

@sales.post("/receipts/", response_model=schemas.ReceiptSchema)
def create_receipt(created_at:datetime, user: schemas.UserPublicSchema = Depends(get_current_user), session: Session = Depends(create_session)):
    receipt = Queries.create_rececipt(created_at=created_at, id_employee=user.id, session=session)
    return schemas.ReceiptSchema.model_validate(receipt)

@sales.post("/sales/")
def insert_sale(
    id_product: int, 
    quintity: int, 
    receipt_id:int,
    session: Session = Depends(create_session), 
    roots: schemas.RootSchema = Depends(get_roots)):
    try:
        if roots.make_sales:
            Queries.insert_sale_with_storage_check(id_product,quintity,receipt_id,session)
            return {"message":"success"}
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")
    except Exception:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Something went wrong")

@sales.get("/categories/",response_model=list[schemas.CategorySchema])
def all_categories(session: Session = Depends(create_session)):
    categories_orm = Queries.all_categories(session)
    categories_schema = [schemas.CategorySchema.model_validate(row) for row in categories_orm]
    return categories_schema

@sales.get("/jobs/",response_model=list[schemas.JobSchema])
def all_jobs(session: Session = Depends(create_session)):
    jobs_orm = Queries.all_jobs(session)
    jobs_schema = [schemas.JobSchema.model_validate(row) for row in jobs_orm]
    return jobs_schema

@sales.get("/receipts/",response_model=list[schemas.ReceiptSchema])
def all_receipts(session: Session = Depends(create_session)):
    receipts_orm = Queries.all_receipts(session)
    receipts_schema = [schemas.ReceiptSchema.model_validate(row) for row in receipts_orm]
    return receipts_schema

@sales.get("/employees/", response_model=list[schemas.UserPublicSchema])
def all_employees(session: Session = Depends(create_session)):
    employees_orm = Queries.all_employees(session)
    employees_schema = [schemas.UserPublicSchema.model_validate(row) for row in employees_orm]
    return employees_schema

@sales.get("/sales/",response_model=list[schemas.SaleSchema])
def all_sales(session: Session = Depends(create_session)):
    sales_orm = Queries.all_sales(session)
    sales_schema = [schemas.SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema

@sales.patch("/employees/")
def add_boss(id:int,boss_id:int, session: Session = Depends(create_session), roots: schemas.RootSchema = Depends(get_roots)):
    if roots.add_boss:
        Queries.add_boss(id,boss_id,session)
        return {"message":"success"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")

@sales.patch("/products/")
def update_product(
    product_id:int,
    price: Optional[int] = None,
    quantity_at_storage: Optional[int] = None,
    session: Session = Depends(create_session), 
    roots: schemas.RootSchema = Depends(get_roots)
    ):
    if roots.add_products:
        Queries.update_product(product_id,price,quantity_at_storage,session)
        return {"massege":"success"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")

@sales.delete("/products/")
def delete_product(id:int, session: Session = Depends(create_session), roots: schemas.RootSchema = Depends(get_roots)):
    if roots.add_products:
        Queries.delete_product(id,session)
        return {"massege":"success"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You can't do this")

@sales.get("/products/{id}", response_model=schemas.ProductSchema)
def product_by_id(id:int, session: Session = Depends(create_session), roots: schemas.RootSchema = Depends(get_roots)):
    return Queries.get_product_by_id(id,session)

@sales.get("/products/filter/", response_model=list[schemas.ProductSchema])
def filtered_products(category_id:int|None, min_price: float = 0, max_price:float = 10**8, session: Session = Depends(create_session), roots: schemas.RootSchema = Depends(get_roots)):
    products_orm = Queries.filtered_products(category_id, min_price, max_price,session)
    products_schema = [schemas.ProductSchema.model_validate(row) for row in products_orm]
    return products_schema

@sales.get("/products/category/", response_model=list[schemas.ProductSchema])
def products_by_category(category_id:int, session: Session = Depends(create_session), roots: schemas.RootSchema = Depends(get_roots)):
    products_orm = Queries.products_by_category(category_id,session)
    products_schema = [schemas.ProductSchema.model_validate(row) for row in products_orm]
    return products_schema

@sales.get("/employee/{id}/sales", response_model=list[schemas.SaleSchema])
def employee_sales(id:int, session: Session = Depends(create_session), roots: schemas.RootSchema = Depends(get_roots)):
    sales_orm = Queries.employee_sales(id,session)
    sales_schema = [schemas.SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema

@sales.get("/sales/filter/", response_model=list[schemas.SaleSchema])
def sales_products(min_sum: int | None = None,
            max_sum: int | None = None,
            min_date: datetime | None = None,
            max_date: datetime | None = None,
            product_id: int | None = None,
            employee_id: int | None = None, 
            session: Session = Depends(create_session), 
            roots: schemas.RootSchema = Depends(get_roots)):
    
    sales_orm = Queries.filtered_sales(session,min_sum,max_sum,min_date,max_date,product_id, employee_id)
    sales_schema = [schemas.SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema

@sales.post("/roots/")
def add_roots(permisions: schemas.RootSchema, session: Session = Depends(create_session), roots: schemas.RootSchema = Depends(get_roots)):
    root_orm = Queries.insert_root(
        permisions.make_sales, permisions.add_categories,
        permisions.add_products, permisions.redact_products,
        permisions.add_jobs, permisions.add_boss, session)
    return schemas.RootSchema.model_validate(root_orm)

@sales.get("/roots/",response_model=list[schemas.RootSchema])
def all_roots(session:Session = Depends(create_session)):
    roots_orm = Queries.get_all_roots(session)
    roots_schema = [schemas.RootSchema.model_validate(row) for row in roots_orm]
    return roots_schema

@sales.get("/sales/receipt/{id_receipt}", response_model=list[schemas.SaleSchema])
def sales_by_receipt(id_receipt:int, session: Session = Depends(create_session)):
    sales_orm = Queries.sales_by_receipt(id_receipt, session)
    sales_schema = [schemas.SaleSchema.model_validate(row) for row in sales_orm]
    return sales_schema

@sales.get("/products/to/buy", response_model=list[schemas.ProductSchema])
def products_to_buy(red_quantity:int, session: Session = Depends(create_session),roots: schemas.RootSchema = Depends(get_roots)):
    if roots.add_products:
        products_orm = Queries.products_to_buy(red_quantity, session)
        product_schema = [schemas.ProductSchema.model_validate(row) for row in products_orm]
        return product_schema
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't do this")
