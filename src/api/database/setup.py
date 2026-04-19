from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import Base, Categories

DB_URL = "sqlite:///database.db"

engine = create_engine(DB_URL, echo=True)

def create_db_and_tables() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

Session = sessionmaker(engine)

create_db_and_tables()
