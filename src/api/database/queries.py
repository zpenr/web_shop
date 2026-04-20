from sqlalchemy import select, Sequence, and_
from database.models import Products, Categories, Jobs, Employees, Receipts, Sales
from database.setup import Session
from datetime import datetime

class Queries:

    @staticmethod
    def all_products() -> Sequence[Products]:
        with Session() as session:
            query = select(Products)
            return session.execute(query).scalars().all()
    
    @staticmethod
    def insert_product(name:str, price: int, id_category:int, quantity_at_storage:int)->None:
        with Session() as session:
            product = Products(name=name, price=price, id_category=id_category,quantity_at_storage=quantity_at_storage)
            session.add(product)
            session.commit()
    
    @staticmethod
    def insert_category(name:str) -> None:
        with Session() as session:
            category = Categories(name=name)
            session.add(category)
            session.commit()
    
    @staticmethod
    def insert_job(name: str, roots:int) -> None:
        with Session() as session:
            job = Jobs(name=name, roots=roots)
            session.add(job)
            session.commit()

    @staticmethod
    def insert_employee(name:str, surname:str, login:str, password:str, id_job) -> None:
        with Session() as session:
            employee = Employees(name=name, surname=surname,login=login,password=password,id_job=id_job)
            session.add(employee)
            session.commit()

    @staticmethod
    def all_employees():
        with Session() as session:
            return session.execute(select(Employees)).scalars().all()
        
    @staticmethod
    def insert_sale(created_at:datetime, id_employee:int, id_product:int, quintity:int) -> bool:
        with Session() as session:
            try:
                receipt = Receipts(created_at=created_at, id_employee=id_employee)
                session.add(receipt)
                session.flush()
                id_receipt = receipt.id
                sale = Sales(id_receipt=id_receipt, id_product=id_product,quintity=quintity)
                session.add(sale)
                session.commit()
                return True
            except: #noqa
                session.rollback()
                return False

    @staticmethod       
    def job_by_id(id:int):
        with Session() as session:
            query = select(Jobs).where(Jobs.id == id)
            return session.execute(query).scalar_one()
        
    @staticmethod
    def empoloyee_by_login(login:str):
        with Session() as session:
            query = select(Employees).where(Employees.login == login)
            return session.execute(query).scalar_one_or_none()
    
    @staticmethod
    def all_categories():
        with Session() as session:
            query = select(Categories)
            return session.execute(query).scalars().all()
    
    @staticmethod
    def add_boss(id:int,boss_id:int):
        with Session() as session:
            employee = session.query(Employees).with_for_update().filter(Employees.id == id).first()
            employee.boss = boss_id
            session.commit()
            

    @staticmethod  
    def all_jobs():
        with Session() as session:
            query = select(Jobs)
            return session.execute(query).scalars().all()

    @staticmethod 
    def all_sales():
        with Session() as session:
            query = select(Sales)
            return session.execute(query).scalars().all()
    
    @staticmethod
    def all_receipts():
        with Session() as session:
            query = select(Receipts)
            return session.execute(query).scalars().all()

    @staticmethod
    def get_boss(id:int):
        with Session() as session:
            query = select(Employees).where(Employees.id == id)
            return session.execute(query).scalar_one_or_none()
    
    @staticmethod
    def get_childrens(id:int):
        with Session() as session:
            query = select(Employees).where(Employees.boss == id)
            return session.execute(query).scalars().all()

    @staticmethod
    def get_childrens_sales(boss_id:int):
        with Session() as session:
            ids = select(Employees.id).where(Employees.boss == boss_id).scalar_subquery()
            subquery = select(Receipts.id).where(Receipts.id_employee.in_(ids)).scalar_subquery()
            query = select(Sales).where(Sales.id_receipt.in_(subquery))
            return session.execute(query).scalars().all()

    @staticmethod
    def dismiss(id:int, boss_id:int):
        with Session() as session:
            employee = session.query(Employees).filter(and_(Employees.id == id, Employees.boss == boss_id)).first()
            session.delete(employee)
            session.commit()
    
    def root_by_id(id:int):
        with Session() as session :
            query = select(Jobs.roots).join(Employees, Jobs.id == Employees.id_job)
            return session.execute(query).scalar_one()