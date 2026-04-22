from fastapi import (APIRouter, 
                     Form, HTTPException, 
                     status, Depends, 
                    )
from database.queries import Queries
from schemas import UserSchema, TokenSchema, UserPublicSchema
from utils import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.setup import create_session
from sqlalchemy.orm import Session

auth = APIRouter(tags=["auth"])
http_bearer = HTTPBearer()

def validate_auth_user(
        login: str = Form(),
        password: str = Form(),
        session: Session = Depends(create_session)
        ):
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid login or password",
    )
    
    user = Queries.empoloyee_by_login(login=login,session=session)

    if user is None:
        raise exc
    
    if jwt.check_pw(password, user.password):
        return user
    raise exc

@auth.post("/login/", response_model=TokenSchema)
def auth_user(user: UserSchema = Depends(validate_auth_user)):
    jwt_payload = {"name":user.name,
                   "surname":user.surname,
                   "login":user.login,
                   "id_job":user.id_job}
    
    access_token = jwt.encode_jwt(jwt_payload)
    return TokenSchema(
        access_token=access_token,
        token_type="Bearer"
    )

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(http_bearer), session: Session = Depends(create_session)):
    token = creds.credentials
    data = jwt.decode_jwt(token)
    return Queries.empoloyee_by_login(data.get("login"),session)


@auth.get("/me/",response_model=UserPublicSchema)
def user_self_info(user = Depends(get_current_user)):
    return UserPublicSchema.model_validate(user)

@auth.get("/permission/")
def is_permission(roots,user = Depends(get_current_user)):
    if roots >= user.roots:
        return {"message":"access is allowed"}
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="Permission denied")
    
@auth.post("/register/", response_model=TokenSchema)
def insert_employee(
    name:str = Form(),
    surname:str = Form(),
    login:str = Form(),
    password:str = Form(),
    password2:str = Form(),
    id_job:int = Form(),
    session: Session = Depends(create_session)
    ):
    if password!=password2:
        raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT,
                             detail="Your passwords don't match")
    
    Queries.insert_employee(name,surname,login,jwt.hash_pw(password),id_job,session)
    jwt_payload = {"name":name,
                   "surname":surname,
                   "login":login,
                   "id_job":id_job,
                   "roots":Queries.job_by_id(id_job,session).roots
                   }
    access_token = jwt.encode_jwt(jwt_payload)

    return TokenSchema(
        access_token=access_token,
        token_type="Bearer"
    )