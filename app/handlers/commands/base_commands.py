from maxo import Router
from maxo.types import BotStarted
from app.database.requests import insert_user

router = Router()

@router.bot_started()
async def bot_started_handler(bot_started: BotStarted) -> None:
    max_id = bot_started.user.user_id
    
    # insert_user теперь возвращает True для нового пользователя и False для существующего
    is_new_user = await insert_user(max_id=max_id)
    
    if is_new_user:
        message = (
            f"Добро пожаловать в бот для знакомств.\n"
            f"Вы успешно зарегистрированы.\n\n"
            f"Наши команды:\n"
            f"/start - Начать поиск\n"
            f"/my_profile - Мой профиль"
        )
    else:
        message = (
            f"С возвращением в бот для знакомств!\n"
            f"Вы уже зарегистрированы.\n\n"
            f"Наши команды:\n"
            f"/start - Начать поиск\n"
            f"/my_profile - Мой профиль"
        )
    
    await bot_started.send_message(message)