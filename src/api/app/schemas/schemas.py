from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    model_config = {"from_attributes": True}


class UserPublicSchema(BaseModel):
    id: int
    name: str
    surname: str
    id_job: int
    boss: int | None = None
    model_config = {"from_attributes": True}


class UserSchema(UserPublicSchema):
    login: str
    permission_id: int
    model_config = {"from_attributes": True}


class JobSchema(BaseModel):
    id: int
    name: str
    permission_id: int
    model_config = {"from_attributes": True}


class CategorySchema(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class ProductSchema(BaseModel):
    id: int
    name: str
    price: int
    quantity_at_storage: int
    category: CategorySchema
    model_config = {"from_attributes": True}


class SaleSchema(BaseModel):
    id: int
    quantity: int
    id_receipt: int
    product: ProductSchema
    receipt: ReceiptSchema
    model_config = {"from_attributes": True}


class ReceiptSchema(BaseModel):
    id: int
    created_at: datetime
    employee: UserPublicSchema
    model_config = {"from_attributes": True}


class PermissionSchema(BaseModel):
    id: int | None = None
    make_sales: bool
    add_categories: bool
    add_products: bool
    redact_products: bool
    add_jobs: bool
    add_boss: bool

    model_config = {"from_attributes": True}
