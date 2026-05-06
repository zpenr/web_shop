import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.config import settings
from api.database.queries import Queries
from api.database.setup import create_session
from sqlalchemy.orm import Session
from api.schemas import RootSchema

def encode_jwt(
        payload: dict,
        key: str = settings.private_key_path.read_text(),
        algoritm: str = settings.algoritm,
        expire_min: int = settings.access_token_exp_min  
        ):
    to_encode = payload.copy()
    expire = datetime.utcnow() + timedelta(minutes=expire_min) 
    to_encode.update(
        exp=expire
    )
    encoded = jwt.encode(payload=payload, key=key, algorithm=algoritm)
    return encoded

def decode_jwt(
        token: str | bytes,
        key: str = settings.public_key_path.read_text(),
        algoritm: str = settings.algoritm):
    decoded = jwt.decode(jwt=token,key=key,algorithms=[algoritm])
    return decoded


def hash_pw(password:str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_pw(password: str, hash_password:str) -> bool:
    return bcrypt.checkpw(password.encode(), hash_password.encode())

http_bearer = HTTPBearer()
def get_roots(
        creds: HTTPAuthorizationCredentials = Depends(http_bearer),
        session: Session = Depends(create_session)
        ) -> RootSchema:
    token_data = decode_jwt(creds.credentials)
    root_orm = Queries.root_by_user_id(token_data.get("id"), session)
    root_schema = RootSchema.model_validate(root_orm)
    return root_schema
