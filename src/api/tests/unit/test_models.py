import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.database.models import Base, Products

@pytest.fixture(scope="module")
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    s = sessionmaker(bind=engine)()
    yield s
    s.close()

def test_product_price_negative_raises():
    with pytest.raises(ValueError):
        product = Products(name="test", price=-10, id_category=1, quantity_at_storage=5) #noqa
        

def test_product_price_zero_ok(session):
    product = Products(name="free", price=0, id_category=1, quantity_at_storage=10)
    session.add(product)
    session.flush()
    assert product.price == 0
    session.rollback()