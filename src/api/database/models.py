import datetime

from sqlalchemy.orm import DeclarativeBase,relationship, Mapped, mapped_column, validates
from sqlalchemy import ForeignKey, DateTime

class Base(DeclarativeBase):
    pass

class Categories(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    products: Mapped[list["Products"]] = relationship(back_populates="category")

class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[int]
    id_category: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    quantity_at_storage: Mapped[int]

    sales: Mapped[list["Sales"]] = relationship(back_populates="product")
    category: Mapped["Categories"] = relationship(back_populates="products")

    @validates("price")
    def validata_price(self, key, price):
        if price < 0:
            raise ValueError("Price must be greater or equal than zero")
        return price
    
class Jobs(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    roots: Mapped[int]

class Employees(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    surname: Mapped[str]
    login: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    id_job: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    boss: Mapped[int|None]

    receipts: Mapped[list["Receipts"]] = relationship(back_populates="employee")

class Receipts(Base):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    id_employee: Mapped[int] = mapped_column(ForeignKey("employees.id"))

    employee: Mapped["Employees"] = relationship(back_populates="receipts")
    sale: Mapped["Sales"] = relationship(back_populates="receipt")

class Sales(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_receipt: Mapped[int] = mapped_column(ForeignKey("receipts.id"))
    id_product: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quintity: Mapped[int]

    receipt: Mapped["Receipts"] = relationship(back_populates="sale")
    product: Mapped["Products"] = relationship(back_populates="sales")