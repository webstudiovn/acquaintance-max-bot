import asyncio
from typing import List, Optional

from maxo import Bot
from maxo.types.photo_attachment import PhotoAttachment

from sqlalchemy import select

from app.database.models.base import async_session_maker
from app.database.models.channel import Channel
from app.database.models.user import User
from app.keyboards.channel_keyboard import reaction_channel_keyboard



async def get_channels() -> List[Channel]:
    async with async_session_maker() as session:
        result = await session.execute(select(Channel))
        return result.scalars().all()


async def get_user_preferences(user_id: int):
    """Возвращает gender и looking_for пользователя."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(User.gender, User.looking_for).where(User.max_id == user_id)
        )
        row = result.one_or_none()
        
        if row is None:
            return None, None
        
        # Явно проверяем, что поля не NULL в БД
        if row.gender is None or row.looking_for is None:
            return None, None
            
        return row.gender, row.looking_for



async def get_profiles(
    exclude_user_id: Optional[int] = None,
    target_gender: Optional[str] = None,
) -> List[User]:
    async with async_session_maker() as session:
        query = select(User)

        if exclude_user_id is not None:
            query = query.where(User.max_id != exclude_user_id)

        # Проверка на наличие target_gender обязательна, иначе фильтр не сработает
        if target_gender is not None:
            # Убедимся, что в базе нет проблем с пробелами, хотя лучше чистить данные при вставке
            query = query.where(User.gender == target_gender.strip())

        result = await session.execute(query)
        profiles = result.scalars().all()
        return profiles




def format_profile_text(profile, index: int) -> str:
    return (
        f"📋 Анкета #{index}\n"
        f"👤 Имя: {profile.name or 'Не указано'}\n"
        f"🎂 Возраст: {profile.age or 'Не указан'}\n"
        f"📍 Город: {profile.city or 'Не указан'}\n"
        f"📝 О себе: {profile.about or 'Не указано'}\n"
        f"📱 Телефон: {profile.phone or 'Не указано'}\n"
        f"📧 Электронная почта: {profile.email or 'Не указано'}\n"
        f'<a href="https://max.ru/u/{profile.link}">Написать</a>'
    )


async def publish_to_channel(
    bot: Bot,
    channel: Channel,
    profiles: List[User],
    delay_seconds: float = 3.0,
) -> None:
    if not profiles:
        await bot.send_message(
            chat_id=channel.channel_id,
            text="Нет анкет для публикации.",
        )
        return


    for i, profile in enumerate(profiles, 1):
        text = format_profile_text(profile, i)
        attachments = []
        # Внутри цикла в publish_to_channel
        

        # Фото
        if profile.photo_id:
            payload_obj = type("PhotoPayload", (), {"token": profile.photo_id})()
            photo = PhotoAttachment(payload=payload_obj)
            attachments.append(photo.to_request())

        # Клавиатура
        kb_attachment = await reaction_channel_keyboard(target_user_id=profile.max_id)
        attachments.append(kb_attachment)

        await bot.send_message(
            chat_id=channel.channel_id,
            text=text,
            attachments=attachments,
        )

        if i < len(profiles):
            await asyncio.sleep(delay_seconds)


async def publish_all_profiles(
    bot: Bot,
    exclude_user_id: Optional[int] = None,
    delay_seconds: float = 3.0,
) -> Optional[str]:
    channels = await get_channels()
    
    # Получаем предпочтения
    caller_looking_for = await get_user_preferences(exclude_user_id) if exclude_user_id else (None, None)
    

    # Безопасно получаем строковое значение
    target_gender_value = caller_looking_for.value 
    
    profiles = await get_profiles(
        exclude_user_id=exclude_user_id,
        target_gender=target_gender_value,
    )

    for channel in channels:
        await publish_to_channel(bot, channel, profiles, delay_seconds=delay_seconds)

    return None
