import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from config import settings
settings.testing = True

from main import app
from database.setup import engine
from database.models import Base

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def manage_db():
    """Очистка и создание таблиц перед каждым тестом."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.mark.parametrize("cat_name", ["Еда", "Напитки", "Десерты"])
def test_insert_category_multiple_times(cat_name):
    """Тестируем POST /categories/ несколько раз."""
    response = client.post("/categories/", params={"name": cat_name})
    assert response.status_code == 200
    assert response.json() == {"message": "success"}

@pytest.mark.parametrize("name, price, qty", [
    ("Кофе", 150, 10),
    ("Чай", 100, 20),
    ("Булка", 50, 5)
])
def test_insert_product_flow(name, price, qty):
    """Тестируем POST /products/ и GET /products/."""
    client.post("/categories/", params={"name": "Общая"})
    
    response = client.post("/products/", params={
        "name": name,
        "price": price,
        "id_category": 1,
        "quantity_at_storage": qty
    })
    assert response.status_code == 200
    
    get_res = client.get("/products/")
    data = get_res.json()
    assert any(item["name"] == name for item in data)

@pytest.mark.parametrize("job_name, emp_data", [
    ("Менеджер", {"name": "Анна", "surname": "Смирнова", "login": "smirnova_a", "password": "123"}),
    ("Повар", {"name": "Игорь", "surname": "Петров", "login": "petrov_i", "password": "qwerty"})
])
def test_employee_flow(job_name, emp_data):
    """Тестируем POST /jobs/ и POST /employees/."""
    client.post("/jobs/", params={"name": job_name})
    
    emp_data["id_job"] = 1
    response = client.post("/employees/", params=emp_data)
    assert response.status_code == 200
    assert response.json() == {"message": "success"}

@pytest.mark.parametrize("quantity", [1, 5, 10])
def test_receipt_and_sale_flow(quantity):
    """Тестируем POST /receipts/ и POST /sales/."""
    client.post("/categories/", params={"name": "Кат1"})
    client.post("/products/", params={"name": "Товар1", "price": 10, "id_category": 1, "quantity_at_storage": 100})
    client.post("/jobs/", params={"name": "Работа1"})
    client.post("/employees/", params={"name": "Э", "surname": "С", "login": "L", "password": "P", "id_job": 1})
    
    now = datetime.now().isoformat()
    receipt_res = client.post("/receipts/", params={"created_at": now, "id_employee": 1})
    assert receipt_res.status_code == 200
    
    sale_res = client.post("/sales/", params={
        "id_receipt": 1,
        "id_product": 1,
        "quintity": quantity
    })
    assert sale_res.status_code == 200