from sqlalchemy import insert, select, Sequence
from database.models import Products, Categories
from database.setup import Session
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
    
