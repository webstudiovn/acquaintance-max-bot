# app/configs/commands.py
from maxo.types import BotCommand

MAIN_MENU_COMMANDS = [
    BotCommand(name="/start", description="Начать подбор пар"),
    BotCommand(name="/my_profile", description="Мой профиль"),
]
