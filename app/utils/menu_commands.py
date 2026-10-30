# В main.py или utils/menu.py
from maxo import Bot
from app.utils.commands import MAIN_MENU_COMMANDS

async def set_main_menu(bot: Bot):
    await bot.edit_my_commands(commands=MAIN_MENU_COMMANDS)
