from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from api.database.models import Base
from api.config import settings
from api.database.queries import Queries

DB_URL = settings.get_db_url()

engine = create_engine(DB_URL, echo=True)

def create_db_and_tables() -> None:
    Base.metadata.create_all(engine)

def drop_db():
    Base.metadata.drop_all(engine)

Session = sessionmaker(engine)
def create_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise 
    finally:
        session.close()

def create_admin():
    session = Session()
    Queries.insert_root(make_sales=True,add_categories=True,add_products=True,redact_products=True,add_jobs=True,add_boss=True, session=session)
    Queries.insert_job("admin", 1,session=session)
    session.commit()

drop_db()
create_db_and_tables()
create_admin()