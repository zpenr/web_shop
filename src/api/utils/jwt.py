import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi import Response
from config import settings

def encode_jwt(
        payload: dict,
        key: str = settings.private_key_path.read_text(),
        algoritm: str = settings.algoritm,
        expire_min: int = settings.access_token_exp_min  
        ):
    to_encode = payload.copy()
    expire = datetime.utcnow() +timedelta(minutes=expire_min) 
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

def set_cookies(response:Response, content:dict):
    for name, value in content.items():
        response.set_cookie(name, value)

def hash_pw(password:str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_pw(password: str, hash_password:str) -> bool:
    return bcrypt.checkpw(password.encode(), hash_password.encode())