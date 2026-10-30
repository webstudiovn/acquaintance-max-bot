from maxo import Router
from maxo.routing.filters import Command
from maxo.types import MessageCreated
from sqlalchemy import select
from maxo.types.photo_attachment import PhotoAttachment

from app.database.models.base import async_session_maker
from app.database.models.user import User
from app.keyboards.payment_keyboad import payment_keyboard

router = Router()

@router.message_created(Command("my_profile"))
async def my_profile(msg: MessageCreated):
    user_max_id = msg.message.sender.user_id

    async with async_session_maker() as session:
        stmt = select(User).where(User.max_id == user_max_id)
        result = await session.execute(stmt)
        user = result.scalars().first()

    # Проверка: если данных о пользователе нет — предлагаем обновиться
    if not user:
        await msg.answer_text(
            "Профиль не найден. Создайте или обновите анкету, чтобы пользоваться сервисом.\n"
            "Отправьте команду: /profile"
        )
        return

    profile_text = (
        f"👤 Ваш профиль\n\n"
        f"Имя: {user.name or 'Не указано'}\n"
        f"Возраст: {user.age or 'Не указано'}\n"
        f"Город: {user.city or 'Не указано'}\n"
        f"О себе: {user.about or 'Нет описания'}\n"
        f"Электронная почта: {user.email or 'Не указана'}\n"
        f"Телефон: {user.phone or 'Не указан'}\n"
        f"Ссылка: {user.link or 'Не указана'}\n"
        f"Дизлайков: {user.dislike}\n"
        f"Осталось мэтчей: {user.matches_count}\n"
        f"\nДля обновления профиля отправьте: /profile"
    )

    # Если есть фото — готовим media, иначе отправляем только текст
    if user.photo_id:
        payload = type("Payload", (), {"token": user.photo_id})()
        photo = PhotoAttachment(payload=payload)
        photo_request = photo.to_request()
        await msg.send_message(media=(photo_request,),
                               text=profile_text,
                               keyboard=payment_keyboard)
    else:
        await msg.answer_text(profile_text, keyboard=payment_keyboard)
