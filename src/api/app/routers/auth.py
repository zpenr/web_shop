from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    status,
    Depends,
)
from api.app.db.queries import Queries
from api.app.schemas.schemas import UserSchema, TokenSchema, UserPublicSchema, PermissionSchema
from api.app.core import security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.app.dependencies import create_session
from sqlalchemy.orm import Session

auth = APIRouter(tags=["auth"])
http_bearer = HTTPBearer()


def validate_auth_user(
    login: str = Form(),
    password: str = Form(),
    session: Session = Depends(create_session),
):
    """Проверяет учётные данные пользователя при входе.

    Args:
        login: Логин пользователя (из формы).
        password: Пароль пользователя (из формы).
        session: Сессия SQLAlchemy (внедряется зависимостью).

    Returns:
        Объект пользователя (модель SQLAlchemy), если аутентификация успешна.

    Raises:
        HTTPException: 401 Unauthorized, если логин не найден или пароль неверен.
    """
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid login or password",
    )

    user = Queries.employee_by_login(login=login, session=session)

    if user is None:
        raise exc

    if security.check_pw(password, user.password):
        return user
    raise exc


@auth.post("/login/", response_model=TokenSchema)
def auth_user(user: UserSchema = Depends(validate_auth_user)):
    """Эндпоинт входа в систему. Возвращает JWT-токен.

    Args:
        user: Валидированный пользователь (внедряется через Depends).

    Returns:
        TokenSchema: Объект, содержащий access_token и token_type.
    """
    jwt_payload = {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "login": user.login,
        "id_job": user.id_job,
    }

    access_token = security.encode_jwt(jwt_payload)
    return TokenSchema(access_token=access_token, token_type="Bearer")


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: Session = Depends(create_session),
) -> UserPublicSchema:
    """Извлекает текущего пользователя из JWT-токена.

    Args:
        creds: Учётные данные HTTP Bearer (токен).
        session: Сессия SQLAlchemy.

    Returns:
        UserPublicSchema: Публичные данные пользователя.

    Raises:
        HTTPException: 401 Unauthorized при невалидном токене или отсутствии пользователя.
    """

    token = creds.credentials
    data = security.decode_jwt(token)
    user = Queries.employee_by_login(data.get("login"), session)
    return UserPublicSchema.model_validate(user)


@auth.get("/me/", response_model=UserPublicSchema)
def user_self_info(user=Depends(get_current_user)):
    """Возвращает информацию о текущем авторизованном пользователе.

    Args:
        user: Пользователь, полученный через get_current_user.

    Returns:
        UserPublicSchema: Данные пользователя.
    """
    return user


@auth.get("/permission/", response_model=PermissionSchema)
def is_permission(
    user: PermissionSchema = Depends(security.get_permissions),
) -> PermissionSchema:
    """Возвращает права доступа текущего пользователя.

    Args:
        user: Права пользователя, полученные через зависимость security.get_permissions.

    Returns:
        PermissionSchema: Схема прав доступа.
    """
    return user


@auth.post("/register/", response_model=TokenSchema)
def insert_employee(
    name: str = Form(),
    surname: str = Form(),
    login: str = Form(),
    password: str = Form(),
    password2: str = Form(),
    id_job: int = Form(),
    session: Session = Depends(create_session)):
    """Регистрирует нового сотрудника и возвращает JWT-токен.

    Args:
        name: Имя сотрудника.
        surname: Фамилия сотрудника.
        login: Логин (должен быть уникальным).
        password: Пароль.
        password2: Повтор пароля для проверки.
        id_job: ID должности (связан с правами).
        session: Сессия SQLAlchemy.

    Returns:
        TokenSchema: JWT-токен для зарегистрированного пользователя.

    Raises:
        HTTPException: 418 I'm a teapot, если пароли не совпадают.
    """
    if password != password2:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Your passwords don't match",
        )

    Queries.insert_employee(
        name, surname, login, security.hash_pw(password), id_job, session
    )
    jwt_payload = {
        "name": name,
        "surname": surname,
        "login": login,
        "id_job": id_job,
    }
    access_token = security.encode_jwt(jwt_payload)

    return TokenSchema(access_token=access_token, token_type="Bearer")
