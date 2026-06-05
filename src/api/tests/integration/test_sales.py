"""
Интеграционные тесты продаж и товаров.

Тестируют эндпоинты:
- POST /products/
- POST /categories/
- POST /sales/
- PATCH /employees/
- PATCH /products/
- DELETE /products/
- GET /products/to/buy
"""
import pytest
from datetime import datetime
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


def _get_login_token(client, login="testuser", password="testpassword"):
    """Получение токена через логин (токен содержит id пользователя)"""
    response = client.post("/auth/login/", data={
        "login": login,
        "password": password
    })
    assert response.status_code == 200
    return response.json()["access_token"]


def _create_limited_user_and_get_token(client, session, login="limited_user"):
    """Создание пользователя без прав и получение токена через логин"""
    permission = Queries.insert_permission(
        make_sales=False, add_categories=False, add_products=False,
        redact_products=False, add_jobs=False, add_boss=False,
        session=session
    )
    session.flush()
    job = Queries.insert_job("limited", permission.id, session)
    session.flush()
    employee = Queries.insert_employee(
        name="Limited", surname="User", login=login,
        password=security.hash_pw("pass123"),
        id_job=job.id, session=session
    )
    session.flush()

    return _get_login_token(client, login, "pass123")


def _create_category(session, name="Electronics"):
    """Создание категории"""
    return Queries.insert_category(name, session)


def _create_product(session, name="Laptop", price=50000, quantity=10, category_id=1):
    """Создание товара"""
    return Queries.insert_product(name, price, category_id, quantity, session)


def _create_receipt(session, created_at, employee_id):
    """Создание чека"""
    return Queries.create_receipt(created_at, employee_id, session)


class TestInsertProduct:
    """Тесты для POST /products/"""

    def test_insert_product_success(self, client, session, auth_header):
        """Успешное создание товара"""
        category = _create_category(session)
        session.flush()

        response = client.post("/products/", params={
            "name": "Laptop",
            "price": 50000,
            "id_category": category.id,
            "quantity_at_storage": 10
        }, headers=auth_header)

        assert response.status_code == 200
        assert response.json()["message"] == "success"

    def test_insert_product_no_permission(self, client, session):
        """Доступ без права add_products"""
        token = _create_limited_user_and_get_token(client, session, "limited_user1")
        category = _create_category(session)
        session.flush()

        response = client.post("/products/", params={
            "name": "Laptop",
            "price": 50000,
            "id_category": category.id,
            "quantity_at_storage": 10
        }, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403


class TestInsertCategory:
    """Тесты для POST /categories/"""

    def test_insert_category_success(self, client, session, auth_header):
        """Успешное создание категории"""
        response = client.post("/categories/", params={
            "name": "Electronics"
        }, headers=auth_header)

        assert response.status_code == 200
        assert response.json()["message"] == "success"

    def test_insert_category_no_permission(self, client, session):
        """Доступ без права add_categories"""
        token = _create_limited_user_and_get_token(client, session, "limited_user2")

        response = client.post("/categories/", params={
            "name": "Electronics"
        }, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403


class TestInsertSale:
    """Тесты для POST /sales/"""

    def test_insert_sale_success(self, client, session, auth_header):
        """Успешное создание продажи"""
        employee = _create_employee_with_permission(session, "seller1", "pass123")
        category = _create_category(session)
        product = _create_product(session, category_id=category.id)
        receipt = _create_receipt(session, datetime.now(), employee.id)
        session.flush()

        response = client.post("/sales/", params={
            "id_product": product.id,
            "quantity": 2,
            "receipt_id": receipt.id
        }, headers=auth_header)

        assert response.status_code == 200
        assert response.json()["message"] == "success"

    def test_insert_sale_no_permission(self, client, session):
        """Доступ без права make_sales"""
        token = _create_limited_user_and_get_token(client, session, "limited_user3")
        employee = _create_employee_with_permission(session, "seller2", "pass123")
        category = _create_category(session)
        product = _create_product(session, category_id=category.id)
        receipt = _create_receipt(session, datetime.now(), employee.id)
        session.flush()

        response = client.post("/sales/", params={
            "id_product": product.id,
            "quantity": 1,
            "receipt_id": receipt.id
        }, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403

    def test_insert_sale_insufficient_quantity(self, client, session, auth_header):
        """Ошибка при недостаточном количестве товара"""
        employee = _create_employee_with_permission(session, "seller3", "pass123")
        category = _create_category(session)
        product = _create_product(session, quantity=5, category_id=category.id)
        receipt = _create_receipt(session, datetime.now(), employee.id)
        session.flush()

        response = client.post("/sales/", params={
            "id_product": product.id,
            "quantity": 10,
            "receipt_id": receipt.id
        }, headers=auth_header)

        assert response.status_code == 409


class TestAddBoss:
    """Тесты для PATCH /employees/"""

    def test_add_boss_success(self, client, session, auth_header):
        """Успешное назначение начальника"""
        boss = _create_employee_with_permission(session, "boss1", "pass123")
        employee = _create_employee_with_permission(session, "employee1", "pass123")
        session.flush()

        response = client.patch("/employees/", params={
            "id": employee.id,
            "boss_id": boss.id
        }, headers=auth_header)

        assert response.status_code == 200
        assert response.json()["message"] == "success"

    def test_add_boss_no_permission(self, client, session):
        """Доступ без права add_boss"""
        token = _create_limited_user_and_get_token(client, session, "limited_user4")
        boss = _create_employee_with_permission(session, "boss2", "pass123")
        employee = _create_employee_with_permission(session, "employee2", "pass123")
        session.flush()

        response = client.patch("/employees/", params={
            "id": employee.id,
            "boss_id": boss.id
        }, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403


class TestUpdateProduct:
    """Тесты для PATCH /products/"""

    def test_update_product_success(self, client, session, auth_header):
        """Успешное обновление товара"""
        category = _create_category(session)
        product = _create_product(session, category_id=category.id)
        session.flush()

        response = client.patch("/products/", params={
            "product_id": product.id,
            "price": 60000,
            "quantity_at_storage": 15
        }, headers=auth_header)

        assert response.status_code == 200
        assert response.json()["message"] == "success"

    def test_update_product_no_permission(self, client, session):
        """Доступ без права add_products"""
        token = _create_limited_user_and_get_token(client, session, "limited_user5")
        category = _create_category(session)
        product = _create_product(session, category_id=category.id)
        session.flush()

        response = client.patch("/products/", params={
            "product_id": product.id,
            "price": 60000
        }, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403


class TestDeleteProduct:
    """Тесты для DELETE /products/"""

    def test_delete_product_success(self, client, session, auth_header):
        """Успешное удаление товара"""
        category = _create_category(session)
        product = _create_product(session, category_id=category.id)
        session.flush()

        response = client.delete("/products/", params={
            "id": product.id
        }, headers=auth_header)

        assert response.status_code == 200
        assert response.json()["message"] == "success"

    def test_delete_product_no_permission(self, client, session):
        """Доступ без права add_products"""
        token = _create_limited_user_and_get_token(client, session, "limited_user6")
        category = _create_category(session)
        product = _create_product(session, category_id=category.id)
        session.flush()

        response = client.delete("/products/", params={
            "id": product.id
        }, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403


class TestProductsToBuy:
    """Тесты для GET /products/to/buy"""

    def test_products_to_buy_success(self, client, session, auth_header):
        """Успешное получение списка товаров для закупки"""
        category = _create_category(session)
        product_low = _create_product(session, name="LowStock", quantity=5, category_id=category.id)
        product_high = _create_product(session, name="HighStock", quantity=100, category_id=category.id)
        session.flush()

        response = client.get("/products/to/buy", params={
            "red_quantity": 10
        }, headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        product_ids = [p["id"] for p in data]
        assert product_low.id in product_ids
        assert product_high.id not in product_ids

    def test_products_to_buy_no_permission(self, client, session):
        """Доступ без права add_products"""
        token = _create_limited_user_and_get_token(client, session, "limited_user7")

        response = client.get("/products/to/buy", params={
            "red_quantity": 10
        }, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403
