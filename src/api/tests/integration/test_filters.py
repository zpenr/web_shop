"""
Интеграционные тесты фильтрации.

Тестируют эндпоинты:
- GET /products/filter/
- GET /products/category/
- GET /employee/{id}/sales
- GET /sales/filter/
"""
import pytest
from datetime import datetime, timedelta
from api.app.db.queries import Queries
from api.app.core import security


def _create_employee_with_permission(session, login="testuser", password="testpassword",
                                     add_products=True, make_sales=True,
                                     add_categories=True, add_boss=True):
    """Вспомогательная функция для создания сотрудника с правами"""
    permission = Queries.insert_permission(
        make_sales=make_sales, add_categories=add_categories, add_products=add_products,
        redact_products=True, add_jobs=True, add_boss=add_boss,
        session=session
    )
    session.flush()
    job = Queries.insert_job("seller", permission.id, session)
    session.flush()
    employee = Queries.insert_employee(
        name="Test", surname="User", login=login,
        password=security.hash_pw(password),
        id_job=job.id, session=session
    )
    session.flush()
    return employee


def _create_category(session, name="Electronics"):
    """Создание категории"""
    return Queries.insert_category(name, session)


def _create_product(session, name="Laptop", price=50000, quantity=10, category_id=1):
    """Создание товара"""
    return Queries.insert_product(name, price, category_id, quantity, session)


def _create_receipt(session, created_at, employee_id):
    """Создание чека"""
    return Queries.create_receipt(created_at, employee_id, session)


def _create_sale(session, id_product, quantity, receipt_id):
    """Создание продажи"""
    return Queries.insert_sale_with_storage_check(id_product, quantity, receipt_id, session)

