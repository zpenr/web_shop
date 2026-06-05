import pytest
from api.app.db.queries import Queries
from api.app.core import security


class TestGetChildrens:
    def _create_boss_with_children(self, session):
        boss_permission = Queries.insert_permission(
            make_sales=True, add_categories=True, add_products=True,
            redact_products=True, add_jobs=True, add_boss=True,
            session=session
        )
        session.flush()
        boss_job = Queries.insert_job("manager", boss_permission.id, session)
        session.flush()
        boss = Queries.insert_employee(
            name="Boss", surname="Bossov", login="boss_user",
            password=security.hash_pw("password123"),
            id_job=boss_job.id, session=session
        )
        session.flush()

        worker_permission = Queries.insert_permission(
            make_sales=True, add_categories=False, add_products=False,
            redact_products=False, add_jobs=False, add_boss=False,
            session=session
        )
        session.flush()
        worker_job = Queries.insert_job("worker", worker_permission.id, session)
        session.flush()

        child1 = Queries.insert_employee(
            name="Child1", surname="One", login="child1",
            password=security.hash_pw("password123"),
            id_job=worker_job.id, session=session
        )
        child1.boss = boss.id
        session.flush()

        child2 = Queries.insert_employee(
            name="Child2", surname="Two", login="child2",
            password=security.hash_pw("password123"),
            id_job=worker_job.id, session=session
        )
        child2.boss = boss.id
        session.flush()

        return boss, [child1, child2]

    def test_get_childrens_success(self, client, session):
        boss, children = self._create_boss_with_children(session)

        response = client.get(f"/manager/childrens/?boss_id={boss.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [item["name"] for item in data]
        assert "Child1" in names
        assert "Child2" in names

    def test_get_childrens_empty(self, client, session):
        permission = Queries.insert_permission(
            make_sales=True, add_categories=True, add_products=True,
            redact_products=True, add_jobs=True, add_boss=True,
            session=session
        )
        session.flush()
        job = Queries.insert_job("manager", permission.id, session)
        session.flush()
        boss = Queries.insert_employee(
            name="Lonely", surname="Boss", login="lonely_boss",
            password=security.hash_pw("password123"),
            id_job=job.id, session=session
        )
        session.flush()

        response = client.get(f"/manager/childrens/?boss_id={boss.id}")

        assert response.status_code == 200
        assert response.json() == []


class TestGetChildrensSales:
    def _create_boss_with_children_and_sales(self, session):
        boss_permission = Queries.insert_permission(
            make_sales=True, add_categories=True, add_products=True,
            redact_products=True, add_jobs=True, add_boss=True,
            session=session
        )
        session.flush()
        boss_job = Queries.insert_job("manager", boss_permission.id, session)
        session.flush()
        boss = Queries.insert_employee(
            name="Boss", surname="Bossov", login="boss_with_sales",
            password=security.hash_pw("password123"),
            id_job=boss_job.id, session=session
        )
        session.flush()

        worker_permission = Queries.insert_permission(
            make_sales=True, add_categories=False, add_products=False,
            redact_products=False, add_jobs=False, add_boss=False,
            session=session
        )
        session.flush()
        worker_job = Queries.insert_job("seller", worker_permission.id, session)
        session.flush()
        child = Queries.insert_employee(
            name="Seller", surname="One", login="seller_child",
            password=security.hash_pw("password123"),
            id_job=worker_job.id, session=session
        )
        child.boss = boss.id
        session.flush()

        from api.app.models.models import Category, Product
        category = Category(name="Test Category")
        session.add(category)
        session.flush()
        product = Product(
            name="Test Product", price=100,
            id_category=category.id, quantity_at_storage=50
        )
        session.add(product)
        session.flush()

        from api.app.models.models import Receipt, Sale
        from datetime import datetime
        receipt = Receipt(created_at=datetime.now(), id_employee=child.id)
        session.add(receipt)
        session.flush()
        sale = Sale(id_receipt=receipt.id, id_product=product.id, quantity=2)
        session.add(sale)
        session.flush()

        return boss, child

    def test_get_childrens_sales_success(self, client, session):
        boss, child = self._create_boss_with_children_and_sales(session)

        response = client.get(f"/manager/sales/?boss_id={boss.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_childrens_sales_empty(self, client, session):
        boss_permission = Queries.insert_permission(
            make_sales=True, add_categories=True, add_products=True,
            redact_products=True, add_jobs=True, add_boss=True,
            session=session
        )
        session.flush()
        boss_job = Queries.insert_job("manager", boss_permission.id, session)
        session.flush()
        boss = Queries.insert_employee(
            name="Boss", surname="NoSales", login="boss_no_sales",
            password=security.hash_pw("password123"),
            id_job=boss_job.id, session=session
        )
        session.flush()

        worker_permission = Queries.insert_permission(
            make_sales=True, add_categories=False, add_products=False,
            redact_products=False, add_jobs=False, add_boss=False,
            session=session
        )
        session.flush()
        worker_job = Queries.insert_job("worker", worker_permission.id, session)
        session.flush()
        child = Queries.insert_employee(
            name="Worker", surname="NoSales", login="worker_no_sales",
            password=security.hash_pw("password123"),
            id_job=worker_job.id, session=session
        )
        child.boss = boss.id
        session.flush()

        response = client.get(f"/manager/sales/?boss_id={boss.id}")

        assert response.status_code == 200
        assert response.json() == []


class TestDismissEmployee:
    def _create_boss_with_child(self, session):
        boss_permission = Queries.insert_permission(
            make_sales=True, add_categories=True, add_products=True,
            redact_products=True, add_jobs=True, add_boss=True,
            session=session
        )
        session.flush()
        boss_job = Queries.insert_job("manager", boss_permission.id, session)
        session.flush()
        boss = Queries.insert_employee(
            name="Boss", surname="Dismiss", login="boss_dismiss",
            password=security.hash_pw("password123"),
            id_job=boss_job.id, session=session
        )
        session.flush()

        worker_permission = Queries.insert_permission(
            make_sales=True, add_categories=False, add_products=False,
            redact_products=False, add_jobs=False, add_boss=False,
            session=session
        )
        session.flush()
        worker_job = Queries.insert_job("worker", worker_permission.id, session)
        session.flush()
        child = Queries.insert_employee(
            name="Worker", surname="ToDismiss", login="worker_dismiss",
            password=security.hash_pw("password123"),
            id_job=worker_job.id, session=session
        )
        child.boss = boss.id
        session.flush()

        return boss, child

    def test_dismiss_employee_success(self, client, session, auth_header):
        boss, child = self._create_boss_with_child(session)

        response = client.delete(
            f"/manager/childrens/?id={child.id}&boss_id={boss.id}",
            headers=auth_header
        )

        assert response.status_code == 200
        assert response.json()["message"] == "success"

        from api.app.models.models import Employee
        deleted_employee = session.query(Employee).filter(Employee.id == child.id).first()
        assert deleted_employee is None

    def test_dismiss_employee_not_own_child(self, client, session):
        """Проверка что boss2 не может уволить child принадлежащего boss1"""
        boss1_permission = Queries.insert_permission(
            make_sales=True, add_categories=True, add_products=True,
            redact_products=True, add_jobs=True, add_boss=True,
            session=session
        )
        session.flush()
        boss1_job = Queries.insert_job("manager1", boss1_permission.id, session)
        session.flush()
        boss1 = Queries.insert_employee(
            name="Boss1", surname="One", login="boss1_test",
            password=security.hash_pw("password123"),
            id_job=boss1_job.id, session=session
        )
        session.flush()

        boss2_permission = Queries.insert_permission(
            make_sales=True, add_categories=True, add_products=True,
            redact_products=True, add_jobs=True, add_boss=True,
            session=session
        )
        session.flush()
        boss2_job = Queries.insert_job("manager2", boss2_permission.id, session)
        session.flush()
        boss2 = Queries.insert_employee(
            name="Boss2", surname="Two", login="boss2_test",
            password=security.hash_pw("password123"),
            id_job=boss2_job.id, session=session
        )
        session.flush()

        worker_permission = Queries.insert_permission(
            make_sales=True, add_categories=False, add_products=False,
            redact_products=False, add_jobs=False, add_boss=False,
            session=session
        )
        session.flush()
        worker_job = Queries.insert_job("worker", worker_permission.id, session)
        session.flush()
        child = Queries.insert_employee(
            name="Worker", surname="Child", login="worker_child_test",
            password=security.hash_pw("password123"),
            id_job=worker_job.id, session=session
        )
        child.boss = boss1.id
        session.flush()

        # Получаем токен для boss2
        response = client.post("/auth/login/", data={
            "login": "boss2_test",
            "password": "password123"
        })
        assert response.status_code == 200
        boss2_token = response.json()["access_token"]

        # boss2 пытается уволить child принадлежащего boss1
        response = client.delete(
            f"/manager/childrens/?id={child.id}&boss_id={boss2.id}",
            headers={"Authorization": f"Bearer {boss2_token}"}
        )

        # Должно вернуть 404 (child не найден среди подчиненных boss2)
        assert response.status_code == 404
