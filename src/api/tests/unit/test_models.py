import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.app.models.models import Base, Product


@pytest.fixture(scope="module")
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    s = sessionmaker(bind=engine)()
    yield s
    s.close()


def test_product_price_negative_raises():
    with pytest.raises(ValueError):
        Product(name="test", price=-10, id_category=1, quantity_at_storage=5)

def test_product_price_zero_ok(session):
    product = Product(name="free", price=0, id_category=1, quantity_at_storage=10)
    session.add(product)
    session.flush()
    assert product.price == 0
    session.rollback()

def test_product_quantity_negative_allowed(session):
    product = Product(name="deficit", price=100, id_category=1, quantity_at_storage=-5)
    session.add(product)
    session.flush()
    assert product.quantity_at_storage == -5
    session.rollback()

def test_product_quantity_large_value(session):
    huge = 2**31 - 1
    product = Product(name="huge", price=1, id_category=1, quantity_at_storage=huge)
    session.add(product)
    session.flush()
    assert product.quantity_at_storage == huge
    session.rollback()
