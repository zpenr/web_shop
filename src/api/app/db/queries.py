from sqlalchemy import select, Sequence, and_
from api.app.models.models import (
    Product,
    Category,
    Job,
    Employee,
    Receipt,
    Sale,
    Permission,
)
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import api.app.core.exceptions as exceptions


class Queries:

    @staticmethod
    def all_products(session: Session) -> Sequence[Product]:
        query = select(Product).options(joinedload(Product.category))
        return session.execute(query).scalars().all()

    @staticmethod
    def insert_product(
        name: str,
        price: int,
        id_category: int,
        quantity_at_storage: int,
        session: Session,
    ) -> Product:
        product = Product(
            name=name,
            price=price,
            id_category=id_category,
            quantity_at_storage=quantity_at_storage,
        )
        session.add(product)
        session.flush()
        return product

    @staticmethod
    def insert_category(name: str, session: Session) -> Category:
        category = Category(name=name)
        session.add(category)
        session.flush()
        return category

    @staticmethod
    def insert_job(name: str, permission_id: int, session: Session) -> Job:
        job = Job(name=name, permission_id=permission_id)
        session.add(job)
        session.flush()
        return job

    @staticmethod
    def insert_employee(
        name: str,
        surname: str,
        login: str,
        password: str,
        id_job: int,
        session: Session,
    ) -> Employee:
        employee = Employee(
            name=name, surname=surname, login=login, password=password, id_job=id_job
        )
        session.add(employee)
        session.flush()
        return employee

    @staticmethod
    def all_employees(session: Session):
        return session.execute(select(Employee)).scalars().all()

    @staticmethod
    def insert_sale_with_storage_check(
        id_product: int, quantity: int, receipt_id: int, session: Session
    ) -> Sale | exceptions.NotEnoughProductException:

        product = session.get(Product, id_product)

        if product.quantity_at_storage >= quantity:
            product.quantity_at_storage -= quantity

            sale = Sale(id_receipt=receipt_id, id_product=id_product, quantity=quantity)

            session.add(sale)
            session.flush()
            return sale

        else:
            raise exceptions.NotEnoughProductException()

    @staticmethod
    def job_by_id(id: int, session: Session):
        query = select(Job).where(Job.id == id)
        return session.execute(query).scalar_one()

    @staticmethod
    def employee_by_login(login: str, session: Session):
        query = select(Employee).where(Employee.login == login)
        return session.execute(query).scalar_one_or_none()

    @staticmethod
    def all_categories(session: Session):
        query = select(Category)
        return session.execute(query).scalars().all()

    @staticmethod
    def add_boss(id: int, boss_id: int, session: Session) -> Employee:
        employee = (
            session.query(Employee).with_for_update().filter(Employee.id == id).first()
        )
        employee.boss = boss_id
        return employee

    @staticmethod
    def all_jobs(session: Session):
        query = select(Job)
        return session.execute(query).scalars().all()

    @staticmethod
    def all_sales(session: Session):
        query = select(Sale).options(
            joinedload(Sale.receipt).joinedload(Receipt.employee),
            joinedload(Sale.product).joinedload(Product.category),
        )
        return session.execute(query).scalars().all()

    @staticmethod
    def all_receipts(session: Session):
        query = select(Receipt).options(joinedload(Receipt.employee))
        return session.execute(query).scalars().all()

    @staticmethod
    def get_boss(id: int, session: Session):
        employee = session.get_one(Employee, id)
        boss = session.get_one(Employee, employee.boss)
        return boss

    @staticmethod
    def get_childrens(id: int, session: Session):
        query = select(Employee).where(Employee.boss == id)
        return session.execute(query).scalars().all()

    @staticmethod
    def get_childrens_sales(boss_id: int, session: Session):
        ids = select(Employee.id).where(Employee.boss == boss_id).scalar_subquery()
        subquery = (
            select(Receipt.id).where(Receipt.id_employee.in_(ids)).scalar_subquery()
        )
        query = (
            select(Sale)
            .where(Sale.id_receipt.in_(subquery))
            .options(
                joinedload(Sale.receipt).joinedload(Receipt.employee),
                joinedload(Sale.product).joinedload(Product.category),
            )
        )
        return session.execute(query).scalars().all()

    @staticmethod
    def dismiss(id: int, boss_id: int, session: Session):
        employee = (
            session.query(Employee)
            .filter(and_(Employee.id == id, Employee.boss == boss_id))
            .first()
        )
        session.delete(employee)
        return employee

    @staticmethod
    def get_product_by_id(id: int, session: Session):
        product = (
            select(Product)
            .where(Product.id == id)
            .options(joinedload(Product.category))
        )
        return session.execute(product).scalar_one()

    @staticmethod
    def update_product(
        id: int, price: int | None, quantity_at_storage: int | None, session: Session
    ) -> Product:
        product = (
            session.query(Product).with_for_update().filter(Product.id == id).first()
        )
        if price is not None:
            product.price = price
        if quantity_at_storage is not None:
            product.quantity_at_storage = quantity_at_storage
        return product

    # ИСПРАВЛЕННЫЙ МЕТОД delete_product
    @staticmethod
    def delete_product(id: int, session: Session) -> dict:
        product = session.query(Product).filter(Product.id == id).first()
        if product is None:
            raise exceptions.NotFoundError(f"Product with id {id} not found")
        session.delete(product)
        return {"message": "Product deleted successfully"}

    @staticmethod
    def filtered_products(
        category_id: int | None,
        min_price: float | None,
        max_price: float | None,
        session: Session,
    ):
        products_query = select(Product).options(joinedload(Product.category))

        conditions = []
        if category_id is not None:
            conditions.append(Product.id_category == category_id)
        if min_price is not None:
            conditions.append(Product.price >= min_price)
        if max_price is not None:
            conditions.append(Product.price <= max_price)

        if conditions:
            products_query = products_query.where(and_(*conditions))

        return session.execute(products_query).scalars().all()

    @staticmethod
    def products_by_category(id_category: int, session: Session):
        products = (
            select(Product)
            .where(Product.id_category == id_category)
            .options(joinedload(Product.category))
        )
        return session.execute(products).scalars().all()

    @staticmethod
    def employee_sales(employee_id: int, session: Session):
        sales = (
            select(Sale)
            .join(Receipt, Receipt.id == Sale.id_receipt)
            .where(Receipt.id_employee == employee_id)
            .options(
                joinedload(Sale.receipt).joinedload(Receipt.employee),
                joinedload(Sale.product).joinedload(Product.category),
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
        employee_id: int | None = None,
    ):

        query = select(Sale)

        need_product_join = (
            min_sum is not None or max_sum is not None or product_id is not None
        )
        need_receipt_join = (
            min_date is not None or max_date is not None or employee_id is not None
        )

        if need_product_join:
            query = query.join(Sale.product)
        if need_receipt_join:
            query = query.join(Sale.receipt)
            if employee_id is not None:
                query = query.join(Receipt.employee)

            if product_id is not None:
                query = query.where(Sale.id_product == product_id)

        if min_sum is not None:
            query = query.where(Product.price * Sale.quantity >= min_sum)

        if max_sum is not None:
            query = query.where(Product.price * Sale.quantity <= max_sum)

        if min_date is not None:
            query = query.where(Receipt.created_at >= min_date)

        if max_date is not None:
            query = query.where(Receipt.created_at <= max_date)

        if employee_id is not None:
            query = query.where(Employee.id == employee_id)

        query = query.options(
            joinedload(Sale.receipt).joinedload(Receipt.employee),
            joinedload(Sale.product).joinedload(Product.category),
        )

        return session.execute(query).unique().scalars().all()

    @staticmethod
    def get_all_permissions(session: Session):
        return session.execute(select(Permission)).scalars().all()

    @staticmethod
    def permission_by_id(permission_id: int, session: Session) -> Permission:
        return session.execute(
            select(Permission).where(Permission.id == permission_id)
        ).scalar_one()

    @staticmethod
    def permission_by_user_id(user_id: int, session: Session):
        query = (
            select(Permission)
            .join(Job, Job.permission_id == Permission.id)
            .join(Employee, Employee.id_job == Job.id)
            .where(Employee.id == user_id)
        )
        return session.execute(query).scalar_one()

    @staticmethod
    def insert_permission(
        make_sales: bool,
        add_categories: bool,
        add_products: bool,
        redact_products: bool,
        add_jobs: bool,
        add_boss: bool,
        session: Session,
    ) -> Permission:
        permission = Permission(
            make_sales=make_sales,
            add_categories=add_categories,
            add_products=add_products,
            redact_products=redact_products,
            add_jobs=add_jobs,
            add_boss=add_boss,
        )
        session.add(permission)
        session.flush()

        return permission

    @staticmethod
    def create_receipt(created_at: datetime, id_employee: int, session: Session):
        receipt = Receipt(created_at=created_at, id_employee=id_employee)
        session.add(receipt)
        session.flush()
        return receipt

    @staticmethod
    def sales_by_receipt(receipt_id: int, session: Session):
        query = (
            select(Sale)
            .join(Receipt, Receipt.id == Sale.id_receipt)
            .where(Receipt.id == receipt_id)
        )
        return session.execute(query).scalars().all()

    @staticmethod
    def products_to_buy(red_quantity: int, session: Session) -> list[Product]:
        query = (
            select(Product)
            .where(Product.quantity_at_storage <= red_quantity)
            .options(joinedload(Product.category))
        )
        return session.execute(query).scalars().all()
