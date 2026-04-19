from sqlalchemy import select, Sequence
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
    def insert_job(name: str) -> None:
        with Session() as session:
            job = Jobs(name=name)
            session.add(job)
            session.commit()

    @staticmethod
    def insert_employee(name:str, surname:str, login:str, password:str, id_job) -> None:
        with Session() as session:
            employee = Employees(name=name, surname=surname,login=login,password=password,id_job=id_job)
            session.add(employee)
            session.commit()

    @staticmethod
    def insert_receipt(created_at:datetime, id_employee:int):
        with Session() as session:
            receipt = Receipts(created_at=created_at, id_employee=id_employee)
            session.add(receipt)
            session.commit()

    @staticmethod
    def insert_sale(id_receipt:int, id_product:int, quintity:int):
        with Session() as session:
            sale = Sales(id_receipt=id_receipt, id_product=id_product,quintity=quintity)
            session.add(sale)
            session.commit()