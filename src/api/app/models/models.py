import datetime

from sqlalchemy.orm import (
    DeclarativeBase,
    relationship,
    Mapped,
    mapped_column,
    validates,
)
from sqlalchemy import ForeignKey, DateTime


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[int]
    id_category: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    quantity_at_storage: Mapped[int]

    sales: Mapped[list["Sale"]] = relationship(back_populates="product")
    category: Mapped["Category"] = relationship(back_populates="products")

    @validates("price")
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price must be greater or equal than zero")
        return price


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    make_sales: Mapped[bool]
    add_categories: Mapped[bool]
    add_products: Mapped[bool]
    redact_products: Mapped[bool]
    add_jobs: Mapped[bool]
    add_boss: Mapped[bool]

    jobs: Mapped[list["Job"]] = relationship(back_populates="permission")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id"))

    permission: Mapped["Permission"] = relationship(back_populates="jobs")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    surname: Mapped[str]
    login: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    id_job: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    boss: Mapped[int | None]

    receipts: Mapped[list["Receipt"]] = relationship(back_populates="employee")


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    id_employee: Mapped[int] = mapped_column(ForeignKey("employees.id"))

    employee: Mapped["Employee"] = relationship(back_populates="receipts")
    sales: Mapped[list["Sale"]] = relationship(back_populates="receipt")


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_receipt: Mapped[int] = mapped_column(ForeignKey("receipts.id"))
    id_product: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]

    receipt: Mapped["Receipt"] = relationship(back_populates="sales")
    product: Mapped["Product"] = relationship(back_populates="sales")
