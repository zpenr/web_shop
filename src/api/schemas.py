from pydantic import BaseModel
from datetime import datetime

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    model_config = {"from_attributes": True}

class UserPublicSchema(BaseModel):
    name: str 
    surname: str
    id_job:int
    model_config = {"from_attributes": True}

class UserSchema(UserPublicSchema):
    login: str
    roots: int
    model_config = {"from_attributes": True}

class JobSchema(BaseModel):
    id: int
    name: int
    roots: int
    model_config = {"from_attributes": True}

class CategorySchema(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}

class ReceiptSchema(BaseModel):
    id:int
    created_at: datetime
    employee: UserPublicSchema
    model_config = {"from_attributes": True}

class ProductSchema(BaseModel):
    id:int
    name:str
    price:int
    quantity_at_storage:int
    category: CategorySchema
    model_config = {"from_attributes": True}

class SaleSchema(BaseModel):
    id:int
    quintity:int
    receipt: ReceiptSchema
    product: ProductSchema
    model_config = {"from_attributes": True}