from fastapi_mail import (
    FastMail,
    ConnectionConfig,
    MessageSchema,
    MessageType,
)


from src.config import settings
from src.database import async_session_maker_null_pool
from src.utils.db_manager import DBManager

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME="Набронировал",
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(conf)


async def send_email(
    email: str,
    subject: str,
    body: str,
):
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype=MessageType.html,
    )

    await fm.send_message(message)


async def send_email_chekin_td(
    user_id: int,
):
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        email = (await db.users.get_one(id=user_id)).email
    await send_email(
        email= email,
        subject="Набронировал",
        body="""
            <h1>Набронировал 🏨</h1>
            <p>Напоминаем, что сегодня у вас заселение</p>
            """,
    )
