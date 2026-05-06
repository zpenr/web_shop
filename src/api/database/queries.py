from sqlalchemy import select, Sequence, and_
from api.database.models import (
                    Products, Categories, Jobs,
                    Employees, Receipts, Sales, Roots)
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import api.exceptions as exceptions

class Queries:

    @staticmethod
    def all_products(session: Session) -> Sequence[Products]:
        query = select(Products).options(joinedload(Products.category))
        return session.execute(query).scalars().all()
    
    @staticmethod
    def insert_product(name:str, price: int, id_category:int, quantity_at_storage:int, session: Session)->Products:
        product = Products(name=name, price=price, id_category=id_category,quantity_at_storage=quantity_at_storage)
        session.add(product)
        session.flush()
        return product
    
    @staticmethod
    def insert_category(name:str, session: Session) -> Categories:
        category = Categories(name=name)
        session.add(category)
        session.flush()
        return category
    
    @staticmethod
    def insert_job(name: str, root_id:int, session: Session) -> Jobs:               
        job = Jobs(name=name, root_id=root_id)
        session.add(job)
        session.flush()
        return job

    @staticmethod
    def insert_employee(name:str, surname:str, login:str, password:str, id_job:int, session: Session) -> Employees:
        employee = Employees(name=name, surname=surname,login=login,password=password,id_job=id_job)
        session.add(employee)
        session.flush()
        return employee

    @staticmethod
    def all_employees(session: Session):
        return session.execute(select(Employees)).scalars().all()
        
    @staticmethod
    def insert_sale_with_storage_check(id_product:int, quintity:int, receipt_id:int, session: Session) -> Sales|exceptions.NotEnougthProductException:
        
        product = session.get(Products, id_product)
        
        if product.quantity_at_storage >= quintity:
            product.quantity_at_storage -= quintity
            

            sale = Sales(id_receipt=receipt_id, id_product=id_product,quintity=quintity)
            
            session.add(sale)
            session.flush()
            return sale
        
        else:
            raise exceptions.NotEnougthProductException()

    @staticmethod       
    def job_by_id(id:int, session: Session):
        query = select(Jobs).where(Jobs.id == id)
        return session.execute(query).scalar_one()
        
    @staticmethod
    def empoloyee_by_login(login:str, session: Session):
        query = select(Employees).where(Employees.login == login)
        return session.execute(query).scalar_one_or_none()
    
    @staticmethod
    def all_categories(session: Session):
        query = select(Categories)
        return session.execute(query).scalars().all()
    
    @staticmethod
    def add_boss(id:int,boss_id:int, session: Session) ->Employees:
        employee = session.query(Employees).with_for_update().filter(Employees.id == id).first()
        employee.boss = boss_id
        return employee 
    
    @staticmethod  
    def all_jobs(session: Session):
        query = select(Jobs)
        return session.execute(query).scalars().all()

    @staticmethod 
    def all_sales(session: Session):
        query = (select(Sales)
                 .options(
                     joinedload(Sales.receipt).joinedload(Receipts.employee),
                     joinedload(Sales.product).joinedload(Products.category)
                     )
                )
        return session.execute(query).scalars().all()
    
    @staticmethod
    def all_receipts(session: Session):
        query = select(Receipts).options(joinedload(Receipts.employee))
        return session.execute(query).scalars().all()

    @staticmethod
    def get_boss(id:int, session: Session):
        query = select(Employees).where(Employees.id == id)
        return session.execute(query).scalar_one_or_none()
    
    @staticmethod
    def get_childrens(id:int, session: Session):
        query = select(Employees).where(Employees.boss == id)
        return session.execute(query).scalars().all()

    @staticmethod
    def get_childrens_sales(boss_id:int, session: Session):
        ids = select(Employees.id).where(Employees.boss == boss_id).scalar_subquery()
        subquery = select(Receipts.id).where(Receipts.id_employee.in_(ids)).scalar_subquery()
        query = (select(Sales)
                 .where(Sales.id_receipt.in_(subquery))
                 .options(
                     joinedload(Sales.receipt).joinedload(Receipts.employee),
                     joinedload(Sales.product).joinedload(Products.category)
                     )
                 )
        return session.execute(query).scalars().all()

    @staticmethod
    def dismiss(id:int, boss_id:int, session: Session):
        employee = session.query(Employees).filter(and_(Employees.id == id, Employees.boss == boss_id)).first()
        session.delete(employee)
        return employee
    
    @staticmethod  
    def get_product_by_id(id:int, session: Session):
        product = (select(Products)
                   .where(Products.id == id)
                   .options(joinedload(Products.category))
                   )
        return session.execute(product).scalar_one()
        
    @staticmethod
    def update_product(id:int, price:int|None, quantity_at_storage:int|None, session: Session) -> Products:
        product = session.query(Products).with_for_update().filter(Products.id == id).first()
        if price is not None:
            product.price = price
        if quantity_at_storage is not None:
            product.quantity_at_storage = quantity_at_storage
        return product
    
    @staticmethod
    def delete_product(id:int, session: Session) -> Products:
        product = session.query(Employees).filter(Products.id == id).first()
        session.delete(product)
        return product
    
    @staticmethod
    def filtered_products(category_id:int|None, min_price: float, max_price:float, session: Session):
        products = (select(Products)
            .where(
                and_(
                    Products.id_category == category_id,
                    Products.price >= min_price,
                    Products.price <= max_price
                    )
                )
                .options(joinedload(Products.category))
                )
        return session.execute(products).scalars().all()
    
    @staticmethod
    def products_by_category(id_category: int, session: Session):
        products = (select(Products)
                    .where(Products.id_category == id_category)
                    .options(joinedload(Products.category))
                    )
        return session.execute(products).scalars().all()

    @staticmethod    
    def employee_sales(employee_id:int, session: Session):
        sales = (select(Sales)
                 .join(Receipts, Receipts.id == Sales.id_receipt)
                 .where(Receipts.id_employee == employee_id)
                 .options(
                     joinedload(Sales.receipt).joinedload(Receipts.employee),
                     joinedload(Sales.product).joinedload(Products.category)
                     )
                 )
        return session.execute(sales).scalars().all()
    
    @staticmethod
    def filtered_sales(
            session: Session,
            min_sum: int | None = None,
            max_sum: int | None = None,
            min_date: datetime | None = None,
            max_date: datetime | None = None,
            product_id: int | None = None,
            employee_id: int | None = None,):
        
        query = select(Sales)

        need_product_join = (min_sum is not None or max_sum is not None or product_id is not None)
        need_receipt_join = (min_date is not None or max_date is not None or employee_id is not None)
        
        if need_product_join:
            query = query.join(Sales.product)
        if need_receipt_join:
            query = query.join(Sales.receipt)
            if employee_id is not None:
                query = query.join(Receipts.employee)

            if product_id is not None:
                query = query.where(Sales.id_product == product_id)

        if min_sum is not None:
            query = query.where(Products.price * Sales.quintity >= min_sum)

        if max_sum is not None:
            query = query.where(Products.price * Sales.quintity <= max_sum)

        if min_date is not None:
            query = query.where(Receipts.created_at >= min_date)

        if max_date is not None:
            query = query.where(Receipts.created_at <= max_date)
        
        if employee_id is not None:
            query = query.where(Employees.id == employee_id)

        query = query.options(
                     joinedload(Sales.receipt).joinedload(Receipts.employee),
                     joinedload(Sales.product).joinedload(Products.category)
                     )

        return session.execute(query).unique().scalars().all()
    
    @staticmethod
    def get_all_roots(session:Session):
        return session.execute(select(Roots)).scalars().all()
    
    @staticmethod
    def root_by_id(root_id: int, session: Session) -> Roots:
        return session.execute(select(Roots).where(Roots.id == root_id)).scalar_one()
    
    @staticmethod
    def root_by_user_id(user_id: int, session: Session):
        query = (select(Roots)
        .join(Jobs, Jobs.root_id == Roots.id)
        .join(Employees, Employees.id_job == Jobs.id)
        .where(Employees.id == user_id))
        return session.execute(query).scalar_one()
    
    @staticmethod
    def insert_root(make_sales: bool,
                    add_categories: bool,
                    add_products: bool,
                    redact_products: bool,
                    add_jobs: bool,
                    add_boss: bool,
                    session:Session) -> Roots:
        roots = Roots(make_sales=make_sales,
                      add_categories=add_categories,
                      add_products=add_products,
                      redact_products=redact_products, 
                      add_jobs=add_jobs,add_boss=add_boss)
        session.add(roots)
        session.flush()

        return roots
    
    @staticmethod
    def create_rececipt(created_at: datetime, id_employee: int, session: Session):
        receipt = Receipts(created_at=created_at,id_employee=id_employee)
        session.add(receipt)
        session.flush()
        return receipt
    
    @staticmethod
    def sales_by_receipt(receipt_id:int, session:Session):
        query = select(Sales).join(Receipts, Receipts.id==Sales.id_receipt).where(Receipts.id == receipt_id)
        return session.execute(query).scalars().all()
    
    @staticmethod
    def products_to_buy(session: Session):
        query = (select(Products)
                    .where(Products.quantity_at_storage<=50)
                    .options(joinedload(Products.category))
                    )
        return session.execute(query)