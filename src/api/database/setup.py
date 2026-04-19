from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import Base, Categories
from config import settings
DB_URL = settings.get_db_url()

engine = create_engine(DB_URL, echo=True)

def create_db_and_tables() -> None:
    Base.metadata.create_all(engine)

Session = sessionmaker(engine)
