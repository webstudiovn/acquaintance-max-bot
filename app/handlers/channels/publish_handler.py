from maxo import Router
from maxo.routing.filters import Command
from maxo.types import MessageCreated
from app.services.publish_service import publish_all_profiles
from maxo import Bot

router = Router()


@router.message_created(Command("publish_profiles"))
async def publish_profiles_to_channels(msg: MessageCreated,
                                       bot: Bot) -> None:
    error_message = await publish_all_profiles(
        bot=bot,
        exclude_user_id=msg.message.sender.user_id,
        delay_seconds=3.0,
    )

    if error_message:
        await msg.answer(error_message)
    else:
        await msg.answer("Анкеты успешно опубликованы в каналы.")
