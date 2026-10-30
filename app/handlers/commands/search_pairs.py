from maxo import Router
from maxo.routing.filters import Command
from maxo.types.photo_attachment import PhotoAttachment
from maxo.types import MessageCreated

from app.database.models.user import User, Gender, LookingFor
from app.database.models.base import async_session_maker
from app.keyboards.reactions_keyboard import reaction_keyboard
from app.filters.users_is_activate import filter_inactive_users
from sqlalchemy import select

router = Router()


@router.message_created(Command("start"))
async def handle_start(msg: MessageCreated) -> None:
    user = await filter_inactive_users(msg)

    if user is None:
        return

    async with async_session_maker() as session:
        await show_profiles_for_user(msg, session, user)


def get_target_gender(looking_for: LookingFor | None) -> Gender | None:
    if looking_for is None:
        return None

    mapping = {
        LookingFor.man: Gender.man,
        LookingFor.woman: Gender.woman,
    }
    return mapping.get(looking_for)


async def show_profiles_for_user(
    msg: MessageCreated,
    session,
    user: User,
) -> None:
    query = (
        select(User)
        .where(User.max_id != user.max_id)          # не показывать себя
        .where(User.dislike == 0)                    # не показывать уже дизлайкнутые
    )

    target_gender = get_target_gender(user.looking_for)
    if target_gender is not None:
        query = query.where(User.gender == target_gender)

    offset = 0
    limit = 5
    query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    profiles = result.scalars().all()

    if not profiles:
        await msg.answer("К сожалению, подходящих анкет сейчас нет.")
        return

    for i, profile in enumerate(profiles, 1):
        pair = (
            f"📋 Анкета #{i}\n"
            f"👤 Имя: {profile.name or 'Не указано'}\n"
            f"🎂 Возраст: {profile.age or 'Не указан'}\n"
            f"📍 Город: {profile.city or 'Не указан'}\n"
            f"📝 О себе: {profile.about or 'Не указано'}\n"
            f"📱 Телефон: {profile.phone or 'Не указано'}\n"
            f"📧 Электронная почта: {profile.email or 'Не указано'}\n"
            f'<a href="https://max.ru/u/{profile.link}">Написать</a>'
        )

        if profile.photo_id:
            payload = type("Payload", (), {"token": profile.photo_id})()
            photo = PhotoAttachment(payload=payload)
            photo_request = photo.to_request()

            await msg.send_message(
                text=pair,
                keyboard=await reaction_keyboard(target_user_id=profile.max_id),
                media=(photo_request,),
            )
        else:
            await msg.answer(text=pair)
