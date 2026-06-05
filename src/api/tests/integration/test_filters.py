"""
интеграцинные тесты для лильтрации и теста эндпоинтов:
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
    """сборка сотрудника с правами вспомогательная функция"""
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
