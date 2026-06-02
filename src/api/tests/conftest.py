import tempfile
import secrets
import pytest
from api.app.core.config import settings
from pathlib import Path

settings.testing = True
settings.test_db_url = "sqlite:///./test.db"
settings.algoritm = "HS256"

secret = secrets.token_hex(32)
tmp_key_file = tempfile.NamedTemporaryFile(delete=False, suffix=".key")
tmp_key_file.write(secret.encode())
tmp_key_file.close()
settings.private_key_path = Path(tmp_key_file.name)
settings.public_key_path = Path(tmp_key_file.name)

from fastapi.testclient import TestClient #noqa
from sqlalchemy import create_engine #noqa
from sqlalchemy.orm import sessionmaker #noqa

from api.app.models.models import Base #noqa
from api.app.db.queries import Queries #noqa
from api.app.main import app #noqa

@pytest.fixture(scope="session")
def engine():
    db_url = settings.get_db_url()
    eng = create_engine(db_url, echo=False)
    yield eng
    eng.dispose()

@pytest.fixture(scope="session", autouse=True)
def create_tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    s = Session()
    yield s
    s.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(session):
    from api.app.db.setup import create_session

    def _override_session():
        yield session

    app.dependency_overrides[create_session] = _override_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def admin_token(client, session):
    root = Queries.insert_root(
        make_sales=True, add_categories=True, add_products=True,
        redact_products=True, add_jobs=True, add_boss=True,
        session=session
    )
    session.flush()
    job = Queries.insert_job("admin", root.id, session)
    session.flush()

    resp = client.post("/auth/register/", data={
        "name": "Admin", "surname": "Adminov",
        "login": "admin", "password": "adminpass",
        "password2": "adminpass", "id_job": job.id
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]

@pytest.fixture(scope="function")
def auth_header(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture(scope="session", autouse=True)
def cleanup_temp_key():
    yield
    import os
    os.unlink(tmp_key_file.name)

    if os.path.exists("./test.db"):
        os.remove("./test.db")