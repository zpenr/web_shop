import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.app.core.config import settings
from api.app.db.queries import Queries
from api.app.dependencies import create_session
from sqlalchemy.orm import Session
from api.app.schemas.schemas import PermissionSchema


def encode_jwt(
    payload: dict,
    key: str = settings.private_key_path.read_text(),
    algoritm: str = settings.algoritm,
    expire_min: int = settings.access_token_exp_min,
):
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_min)
    to_encode.update(exp=expire)
    encoded = jwt.encode(payload=to_encode, key=key, algorithm=algoritm)
    return encoded


def decode_jwt(
    token: str | bytes,
    key: str = settings.public_key_path.read_text(),
    algoritm: str = settings.algoritm,
):
    decoded = jwt.decode(jwt=token, key=key, algorithms=[algoritm])
    return decoded


def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_pw(password: str, hash_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash_password.encode())


http_bearer = HTTPBearer()


def get_permissions(
    creds: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: Session = Depends(create_session),
) -> PermissionSchema:
    token_data = decode_jwt(creds.credentials)
    permission_orm = Queries.permission_by_user_id(token_data.get("id"), session)
    permission_schema = PermissionSchema.model_validate(permission_orm)
    return permission_schema
