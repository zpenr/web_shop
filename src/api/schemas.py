from pydantic import BaseModel

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class UserSchema(BaseModel):
    name: str 
    surname: str
    login: str
    id_job: int
    roots: int