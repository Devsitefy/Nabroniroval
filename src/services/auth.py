from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from src.config import settings
from src.exceptions import UserAlreadyExistsException, InvalidTokenException, UserNotFoundException, \
    InvalidPasswordException, InvalidUserException
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.base import BaseService
from src.services.validator import ValidatorService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(
        self,
        data: dict,
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM
            )
        except jwt.exceptions.InvalidTokenError:
            raise InvalidTokenException

    """-------------------------------------------------------------------------------------------------------"""

    async def register_user(
            self,
            data: UserRequestAdd,
    ):
        hashed_password = AuthService().hash_password(data.password)
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
        try:
            await self.db.users.add(new_user_data)
            await self.db.commit()
        except IntegrityError:
            raise UserAlreadyExistsException

    async def login_user(
            self,
            data: UserRequestAdd,
    ):
        user = await self.db.users.get_user_with_hashed_password(email=data.email)
        if not user:
            raise InvalidUserException
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise InvalidPasswordException
        access_token = AuthService().create_access_token({"user_id": user.id})
        return access_token

    async def get_me(self, user_id: int):
        return await ValidatorService(self.db)(
            self.db.users,
            id=user_id,
        )

