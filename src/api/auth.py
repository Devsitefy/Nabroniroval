from fastapi import APIRouter, Response


from src.api.dependencies import DBDep, UserIdDep
from src.schemas.users import UserRequestAdd
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Аутентификация и Авторизация"])


@router.post("/register", summary="Регистрация")
async def register_user(
    db: DBDep,
    data: UserRequestAdd,
):
    await AuthService(db).register_user(data)
    return {"status": "ok"}

@router.post("/login", summary="Авторизация")
async def login_user(
    db: DBDep,
    data: UserRequestAdd,
    response: Response,
):
    access_token = await AuthService(db).login_user(data)
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.get("/me", summary="получение активного пользователя")
async def get_me(db: DBDep, user_id: UserIdDep):
    user = await AuthService(db).get_me(user_id)
    return {"user": user}


@router.post("/logout", summary="выход из авторизации")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"status": "ok"}
