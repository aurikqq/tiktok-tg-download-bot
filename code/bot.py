import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

token = '7924001209:AAGdhtUa-C-YHs0XFyB0BPY4GV2LVDmSL9g'

allowlist = {
    1104899353 : 'admin',
    5433731633 : 'admin',
    6668023008 : 'admin'
}

session = AiohttpSession(api = TelegramAPIServer.from_base('http://localhost:8099'))
bot = Bot(token, default = DefaultBotProperties(parse_mode = ParseMode.HTML), session = session)
dp = Dispatcher()

@dp.message(CommandStart())
async def send_welcome(message: Message):
    if (allowlist[message.from_user.id] == 'admin'):
        await message.reply("<b>На месте!</b>\n\nАдмин-панель скоро будет, команды ты и так знаешь, всё работает прилежно! (наверное...)")
    elif (allowlist[message.from_user.id] == 'user'):
        await message.reply(f"<b>Приветствую!</b>\nТы - один из {len(allowlist)} юзеров, которые могут пользоваться ботом. Вот что тебе доступно:\n\n <b>/yt</b> - скачать видео с Ютуба\n\nПодробнее в /help.")
    else:
        await message.reply("Ботом можно пользоваться лишь по разрешению владельца.")

        
async def main() -> None:
    bot = Bot(token, default = DefaultBotProperties(parse_mode = ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    asyncio.run(main())