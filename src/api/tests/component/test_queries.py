import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from api.app.db.queries import Queries
from api.app.models.models import (
    Category, Product, Permission, Job, Employee, Receipt, Sale
)
import api.app.core.exceptions as exceptions


@pytest.fixture
def sample_data(session: Session):
    cat = Category(name="Food")
    session.add(cat)
    session.flush()

    prod1 = Product(name="Bread", price=50, id_category=cat.id, quantity_at_storage=100)
    prod2 = Product(name="Milk", price=80, id_category=cat.id, quantity_at_storage=10)
    session.add_all([prod1, prod2])
    session.flush()

    permission = Permission(
        make_sales=True, add_categories=True, add_products=True,
        redact_products=True, add_jobs=True, add_boss=True
    )
    session.add(permission)
    session.flush()

    job = Job(name="Seller", permission_id=permission.id)
    session.add(job)
    session.flush()

    emp1 = Employee(name="Boss", surname="Bossov", login="boss", password="hash", id_job=job.id)
    session.add(emp1)
    session.flush()

    emp2 = Employee(
        name="Ivan", surname="Ivanov", login="ivan", password="hash", id_job=job.id, boss=emp1.id
    )
    session.add(emp2)
    session.flush()

    rcp = Receipt(created_at=datetime.now(), id_employee=1)
    session.add(rcp)
    session.flush()

    sale = Sale(id_receipt=1, id_product=1, quantity=10)
    session.add(sale)
    session.flush()

    return {
        "cat": cat, "prod1": prod1, "prod2": prod2,
        "emp1": emp1, "emp2": emp2, "job": job,
        "permission": permission, "rcp": rcp, "sale": sale
    }


def test_all_products_with_category(session, sample_data):
    products = Queries.all_products(session)
    assert len(products) == 2
    assert products[0].category.name == "Food"


def test_insert_sale_with_storage_check_success(session, sample_data):
    Queries.create_receipt(datetime.now(), sample_data["emp2"].id, session)
    session.flush()
    result = Queries.insert_sale_with_storage_check(sample_data["prod1"].id, 5, 1, session)
    session.flush()
    assert result.id_product == sample_data["prod1"].id
    prod = session.get(Product, sample_data["prod1"].id)
    assert prod.quantity_at_storage == 95


def test_insert_sale_insufficient_quantity(session, sample_data):
    with pytest.raises(exceptions.NotEnoughProductException):
        Queries.create_receipt(datetime.now(), sample_data["emp2"].id, session)
        session.flush()
        Queries.insert_sale_with_storage_check(sample_data["prod2"].id, 20, 1, session)  # noqa


def test_get_childrens(session, sample_data):
    emp = sample_data["emp2"]
    emp.boss = 99
    session.flush()
    children = Queries.get_childrens(99, session)
    assert len(children) == 1
    assert children[0].id == emp.id


@pytest.mark.parametrize("name", [("name1")])
def test_insert_category(name, session):
    assert Queries.insert_category(name, session).name == name


def test_all_employees(session, sample_data):
    assert len(Queries.all_employees(session)) == 2


def test_job_by_id(session, sample_data):
    assert Queries.job_by_id(2, session).name == sample_data["job"].name


def test_employee_by_login(session, sample_data):
    employee = Queries.employee_by_login(login=sample_data["emp2"].login, session=session)
    assert employee.login == sample_data["emp2"].login


def test_all_categories(session, sample_data):
    assert len(Queries.all_categories(session)) == 1


def test_all_jobs(session, sample_data):
    assert len(Queries.all_jobs(session)) == 2


def test_get_product_by_id(session, sample_data):
    product = Queries.get_product_by_id(id=sample_data["prod1"].id, session=session)
    assert product.id == sample_data["prod1"].id


@pytest.mark.parametrize("id, price, quantity_at_storage", [
    (1, None, 100),
    (1, 10, 90),
    (2, 15, None)
])
def test_update_product(id, price, quantity_at_storage, session, sample_data):
    upd_product = Queries.update_product(id, price, quantity_at_storage, session)
    assert upd_product.price == price if price is not None else True
    assert upd_product.quantity_at_storage == quantity_at_storage if quantity_at_storage is not None else True


@pytest.mark.parametrize("category_id, min_price, max_price", [
    (1, 10, 100),
    (1, 50, 60),
    (1, 60, 90),
    (None, 10, 100),
    (1, 50, None),
    (None, None, None),
    (1, None, 60)
])
def test_filtered_products(category_id, min_price, max_price, session, sample_data):
    products = Queries.filtered_products(category_id, min_price, max_price, session)
    for product in products:
        assert product.id_category == category_id if category_id is not None else True
        assert product.price <= max_price if max_price is not None else True
        assert product.price >= min_price if min_price is not None else True


def test_products_by_category(session, sample_data):
    products = Queries.products_by_category(1, session)
    for product in products:
        assert product.id_category == 1


def test_employee_sales(session, sample_data):
    sales = Queries.employee_sales(1, session)
    for sale in sales:
        assert sale.receipt.id_employee == 1


@pytest.mark.parametrize("min_sum, max_sum, min_date, max_date, product_id, employee_id", [
    (None, None, None, None, None, None),
    (400, 600, None, None, 1, 1),
    (400, 600, None, None, 1, None),
    (400, None, None, None, 1, None)
])
def test_filtered_sales(min_sum, max_sum, min_date, max_date, product_id, employee_id, session, sample_data):
    sales = Queries.filtered_sales(session, min_sum, max_sum, min_date, max_date, product_id, employee_id)
    for sale in sales:
        s = sale.quantity * sale.product.price
        assert s >= min_sum if min_sum is not None else True
        assert s <= max_sum if max_sum is not None else True
        assert sale.receipt.created_at >= min_date if min_date is not None else True
        assert sale.receipt.created_at <= max_date if max_date is not None else True
        assert sale.receipt.id_employee == employee_id if employee_id is not None else True
        assert sale.id_product == product_id if product_id is not None else True


def test_all_sales(session, sample_data):
    assert len(Queries.all_sales(session)) == 1


def test_all_receipts(session, sample_data):
    assert len(Queries.all_receipts(session)) == 1


def test_get_boss(session, sample_data):
    assert Queries.get_boss(sample_data["emp2"].id, session).id == 1


def test_get_all_permissions(session, sample_data):
    assert len(Queries.get_all_permissions(session)) == 2


def test_permission_by_id(session, sample_data):
    assert Queries.permission_by_id(1, session).id == 1


@pytest.mark.parametrize("id, target_id", [(1, 2)])
def test_permission_by_user_id(id, target_id, session, sample_data):
    res = Queries.permission_by_user_id(id, session)
    assert res.id == target_id


@pytest.mark.parametrize("make_sales, add_categories, add_products, redact_products, add_jobs, add_boss", [
    (True, True, False, True, True, False)
])
def test_insert_permission(make_sales, add_categories,
                           add_products, redact_products,
                           add_jobs, add_boss,
                           session, sample_data):
    permission = Queries.insert_permission(
        make_sales, add_categories,
        add_products, redact_products,
        add_jobs, add_boss, session
    )

    assert permission.make_sales == make_sales
    assert permission.add_categories == add_categories
    assert permission.add_products == add_products
    assert permission.redact_products == redact_products
    assert permission.add_jobs == add_jobs
    assert permission.add_boss == add_boss


@pytest.mark.parametrize("boss_id", [(1)])
def test_get_childrens_sales(boss_id, session, sample_data):
    sales = Queries.get_childrens_sales(boss_id, session)
    for sale in sales:
        assert sale.receipt.employee.boss == boss_id


@pytest.mark.parametrize("id, boss_id", [(2, 1)])
def test_add_boss(id, boss_id, session, sample_data):
    assert Queries.add_boss(id, boss_id, session).boss == boss_id


@pytest.mark.parametrize("receipt_id", [(1)])
def test_sales_by_receipt(receipt_id, session, sample_data):
    sales = Queries.sales_by_receipt(receipt_id, session)
    for sale in sales:
        assert sale.id_receipt == receipt_id


@pytest.mark.parametrize("name, price, id_category, quantity_at_storage", [
    ("name", 100, 1, 10)
])
def test_insert_product(name, price, id_category, quantity_at_storage, session, sample_data):
    product = Queries.insert_product(name, price, id_category, quantity_at_storage, session)
    assert product.name == name
    assert product.price == price
    assert product.id_category == id_category
    assert product.quantity_at_storage == quantity_at_storage


@pytest.mark.parametrize("name, permission_id", [("name", 1)])
def test_insert_job(name, permission_id, session, sample_data):
    job = Queries.insert_job(name, permission_id, session)
    assert job.name == name
    assert job.permission_id == permission_id


@pytest.mark.parametrize("name, surname, login, password, id_job", [
    ("name", "surname", "login", "password", 1)
])
def test_insert_employee(name, surname, login, password, id_job, session):
    employee = Queries.insert_employee(name, surname, login, password, id_job, session)
    assert employee.name == name
    assert employee.surname == surname
    assert employee.login == login
    assert employee.password == password
    assert employee.id_job == id_job


@pytest.mark.parametrize("red_quantity", [(50)])
def test_products_to_buy(red_quantity, session, sample_data):
    products = Queries.products_to_buy(red_quantity, session)
    for product in products:
        assert product.quantity_at_storage <= red_quantity
