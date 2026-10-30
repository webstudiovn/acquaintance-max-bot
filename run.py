import logging
from maxo.transport.long_polling import LongPolling
from maxo import Bot, Dispatcher
from maxo.enums import TextFormat
from maxo.bot.defaults import BotDefaults
# польз. импоты
from app.configs.settings import settings
from app.utils.menu_commands import set_main_menu
from app.handlers import router


bot = Bot(settings.max.token,
          defaults=BotDefaults(text_format=TextFormat.HTML,
                               disable_link_preview=True))
dp = Dispatcher()

def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    dp.include_router(router)
    dp.after_startup.register(set_main_menu)
    LongPolling(dp).run(bot)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exit...")