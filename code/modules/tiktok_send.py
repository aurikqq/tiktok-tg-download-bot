from aiogram.types import FSInputFile
from tiktokdl.download_post import get_post
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from tiktokdl.post_data import TikTokVideo, TikTokSlide

token = '7924001209:AAGdhtUa-C-YHs0XFyB0BPY4GV2LVDmSL9g'

session = AiohttpSession(api = TelegramAPIServer.from_base('http://localhost:8099'))
bot = Bot(token, default = DefaultBotProperties(parse_mode = ParseMode.HTML), session = session)

async def send_tiktok(url: str):
    file = await get_post(url)
    input_file = FSInputFile(file.file_path)
    if isinstance(file, TikTokSlide):
        await bot.send_photo(1104899353, input_file)
    else:
        await bot.send_video(1104899353, input_file, caption = "<b>Готово!</b>\nВидео, отправленное тобой в Тикток, скачано.")
