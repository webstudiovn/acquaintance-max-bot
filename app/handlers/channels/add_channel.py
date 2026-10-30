from sqlalchemy import select
from maxo import Router
from maxo.types import BotAddedToChat
from app.database.models.channel import Channel
from app.database.models.base import async_session_maker

router = Router()

@router.bot_added_to_chat()
async def on_bot_added(event: BotAddedToChat):
    # event.chat_id — это и есть ID канала/чата (может быть отрицательным)
    channel_id = event.chat_id

    async with async_session_maker() as session:
        # сначала проверяем, нет ли уже такого канала
        result = await session.execute(
            select(Channel).where(Channel.channel_id == channel_id)
        )
        existing = result.scalars().first()

        if existing:
            # уже есть — можно обновить title, если нужно
            existing.title = event.chat_title or "Без названия"
            await session.commit()
            return

        # добавляем новый канал
        new_channel = Channel(
            channel_id=channel_id,
        )
        session.add(new_channel)
        await session.commit()
