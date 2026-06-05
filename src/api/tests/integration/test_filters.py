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


class TestFilterProducts:
    """Тесты для GET /products/filter/"""

    def test_filter_products_by_category(self, client, session, auth_header):
        """Фильтрация по категории"""
        category1 = _create_category(session, "Electronics")
        category2 = _create_category(session, "Clothing")
        product1 = _create_product(session, name="Laptop", category_id=category1.id)
        product2 = _create_product(session, name="Phone", category_id=category1.id)
        product3 = _create_product(session, name="Shirt", category_id=category2.id)
        session.flush()

        response = client.get("/products/filter/", params={
            "category_id": category1.id
        }, headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        product_ids = [p["id"] for p in data]
        assert product1.id in product_ids
        assert product2.id in product_ids
        assert product3.id not in product_ids

    def test_filter_products_by_price_range(self, client, session, auth_header):
        """Фильтрация по диапазону цен"""
        category = _create_category(session)
        product1 = _create_product(session, name="Cheap", price=100, category_id=category.id)
        product2 = _create_product(session, name="Medium", price=500, category_id=category.id)
        product3 = _create_product(session, name="Expensive", price=1000, category_id=category.id)
        session.flush()

        response = client.get("/products/filter/", params={
            "min_price": 200,
            "max_price": 600
        }, headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == product2.id

    def test_filter_products_combined(self, client, session, auth_header):
        """Комбинированная фильтрация"""
        category1 = _create_category(session, "Electronics")
        category2 = _create_category(session, "Clothing")
        product1 = _create_product(session, name="Cheap Electronics", price=100, category_id=category1.id)
        product2 = _create_product(session, name="Expensive Electronics", price=1000, category_id=category1.id)
        product3 = _create_product(session, name="Cheap Clothing", price=100, category_id=category2.id)
        session.flush()

        response = client.get("/products/filter/", params={
            "category_id": category1.id,
            "min_price": 500,
            "max_price": 1500
        }, headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == product2.id


class TestProductsByCategory:
    """Тесты для GET /products/category/"""

    def test_products_by_category(self, client, session, auth_header):
        """Получение товаров по категории"""
        category1 = _create_category(session, "Electronics")
        category2 = _create_category(session, "Clothing")
        product1 = _create_product(session, name="Laptop", category_id=category1.id)
        product2 = _create_product(session, name="Phone", category_id=category1.id)
        product3 = _create_product(session, name="Shirt", category_id=category2.id)
        session.flush()

        response = client.get("/products/category/", params={
            "category_id": category1.id
        }, headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        product_ids = [p["id"] for p in data]
        assert product1.id in product_ids
        assert product2.id in product_ids
        assert product3.id not in product_ids

    def test_products_by_category_empty(self, client, session, auth_header):
        """Пустой список для несуществующей категории"""
        response = client.get("/products/category/", params={
            "category_id": 99999
        }, headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestEmployeeSales:
    """Тесты для GET /employee/{id}/sales"""

    def test_employee_sales(self, client, session, auth_header):
        """Получение продаж конкретного сотрудника"""
        employee1 = _create_employee_with_permission(session, "seller1", "pass123")
        employee2 = _create_employee_with_permission(session, "seller2", "pass123")
        category = _create_category(session)
        product = _create_product(session, category_id=category.id)

        receipt1 = _create_receipt(session, datetime.now(), employee1.id)
        receipt2 = _create_receipt(session, datetime.now(), employee2.id)
        session.flush()

        sale1 = _create_sale(session, product.id, 1, receipt1.id)
        sale2 = _create_sale(session, product.id, 1, receipt2.id)
        session.flush()

        response = client.get(f"/employee/{employee1.id}/sales", headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == sale1.id

    def test_employee_sales_empty(self, client, session, auth_header):
        """Пустой список для сотрудника без продаж"""
        employee = _create_employee_with_permission(session, "seller_empty", "pass123")
        session.flush()

        response = client.get(f"/employee/{employee.id}/sales", headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


