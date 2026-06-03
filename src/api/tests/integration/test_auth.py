"""
Интеграционные тесты аутентификации.

Тестируют эндпоинты:
- POST /auth/login/
- POST /auth/register/
- GET /auth/me/
- GET /auth/permission/
"""
import pytest
from api.app.db.queries import Queries
from api.app.core import security


class TestLogin:
    """Тесты для POST /auth/login/"""

    def _create_employee(self, session, login="testuser", password="testpassword"):
        permission = Queries.insert_permission(
            make_sales=True, add_categories=True, add_products=True,
            redact_products=True, add_jobs=True, add_boss=True,
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

    def test_login_success(self, client, session):
        """Успешный вход с правильными учетными данными"""
        self._create_employee(session, "testuser", "testpassword")

        response = client.post("/auth/login/", data={
            "login": "testuser",
            "password": "testpassword"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"

    def test_login_wrong_password(self, client, session):
        """Неудачный вход с неверным паролем"""
        self._create_employee(session, "testuser2", "testpassword")

        response = client.post("/auth/login/", data={
            "login": "testuser2",
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid login or password"

    def test_login_wrong_login(self, client, session):
        """Неудачный вход с несуществующим логином"""
        response = client.post("/auth/login/", data={
            "login": "nonexistentuser",
            "password": "anypassword"
        })

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid login or password"

    def test_login_response_format(self, client, session):
        """Проверка формата ответа при успешном входе"""
        self._create_employee(session, "formatuser", "testpassword")

        response = client.post("/auth/login/", data={
            "login": "formatuser",
            "password": "testpassword"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        assert data["token_type"] == "Bearer"


class TestRegister:
    """Тесты для POST /auth/register/"""

    def _create_job(self, session):
        permission = Queries.insert_permission(
            make_sales=True, add_categories=True, add_products=True,
            redact_products=True, add_jobs=True, add_boss=True,
            session=session
        )
        session.flush()
        job = Queries.insert_job("seller", permission.id, session)
        session.flush()
        return job

    def test_register_success(self, client, session):
        """Успешная регистрация нового пользователя"""
        job = self._create_job(session)

        response = client.post("/auth/register/", data={
            "name": "New",
            "surname": "User",
            "login": "newuser",
            "password": "newpassword123",
            "password2": "newpassword123",
            "id_job": job.id
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"

    def test_register_passwords_mismatch(self, client, session):
        """Ошибка при несовпадении паролей"""
        job = self._create_job(session)

        response = client.post("/auth/register/", data={
            "name": "Mismatch",
            "surname": "User",
            "login": "mismatchuser",
            "password": "password123",
            "password2": "differentpassword",
            "id_job": job.id
        })

        assert response.status_code == 418
        assert response.json()["detail"] == "Your passwords don't match"

    @pytest.mark.xfail(reason="Баг: IntegrityError не обрабатывается, возвращает 500 вместо 409")
    def test_register_existing_login_returns_409(self, client, session):
        """Регистрация с существующим логином должна возвращать 409 Conflict"""
        job = self._create_job(session)

        response1 = client.post("/auth/register/", data={
            "name": "First",
            "surname": "User",
            "login": "existinglogin",
            "password": "password123",
            "password2": "password123",
            "id_job": job.id
        })
        assert response1.status_code == 200

        response2 = client.post("/auth/register/", data={
            "name": "Second",
            "surname": "User",
            "login": "existinglogin",
            "password": "password456",
            "password2": "password456",
            "id_job": job.id
        })

        assert response2.status_code == 409


class TestGetCurrentUser:
    """Тесты для GET /auth/me/"""

    def test_get_current_user_success(self, client, auth_header):
        """Успешное получение информации о текущем пользователе"""
        response = client.get("/auth/me/", headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "surname" in data
        assert "id_job" in data

    def test_get_current_user_no_token(self, client):
        """Доступ без токена"""
        response = client.get("/auth/me/")

        assert response.status_code == 401

    @pytest.mark.xfail(reason="Баг: некорректный JWT вызывает 500 вместо 401")
    def test_get_current_user_malformed_token(self, client):
        """Доступ с некорректным форматом токена должен возвращать 401"""
        response = client.get("/auth/me/", headers={
            "Authorization": "Bearer not.a.valid.jwt.token"
        })

        assert response.status_code == 401


class TestGetPermissions:
    """Тесты для GET /auth/permission/"""

    def test_get_permissions_no_token(self, client):
        """Доступ без токена"""
        response = client.get("/auth/permission/")

        assert response.status_code == 401

    @pytest.mark.xfail(reason="Баг: permission_by_user_id не находит права для нового пользователя")
    def test_get_permissions_with_valid_token(self, client, session):
        """Получение прав с валидным токеном"""
        permission = Queries.insert_permission(
            make_sales=True, add_categories=False, add_products=False,
            redact_products=False, add_jobs=False, add_boss=False,
            session=session
        )
        session.flush()
        job = Queries.insert_job("cashier", permission.id, session)
        session.flush()

        reg_response = client.post("/auth/register/", data={
            "name": "Cashier",
            "surname": "User",
            "login": "cashier_user",
            "password": "password123",
            "password2": "password123",
            "id_job": job.id
        })
        assert reg_response.status_code == 200
        token = reg_response.json()["access_token"]

        response = client.get("/auth/permission/", headers={
            "Authorization": f"Bearer {token}"
        })

        assert response.status_code == 200
        data = response.json()
        assert "make_sales" in data
        assert data["make_sales"] is True
        assert data["add_categories"] is False
