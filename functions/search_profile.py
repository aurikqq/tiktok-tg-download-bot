import os
import time

from aiogram import Bot, Dispatcher
from aiogram.types import Message, LinkPreviewOptions
from aiogram.enums import ChatMemberStatus
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from .profile import profile


load_dotenv()
bot_token = os.getenv('token')
cluster = AsyncIOMotorClient(os.getenv('db_link'))
chat_id = os.getenv('chat_id')
profile_collection = cluster.proj_one.profiles
ideas_collection = cluster.proj_one.ideas

bot = Bot(token = bot_token, parse_mode = "html")
dp = Dispatcher()

async def search_profile(message: Message):
    global profile_data, kb_profile, inchat_status

    if len(message.text) > len('/find'):
        response = await message.reply('Поиск...')
        arg = message.text.split('/find ', 1)[1]

        if arg.isdigit():
            profile_data = await profile_collection.find_one({"_id": int(arg)})
            arg_type = "ID"
        elif not arg.isdigit():
            profile_data = await profile_collection.find_one({"nick": arg})
            arg_type = "нику"
            if not profile_data:
                username = arg.replace("@", "")
                profile_data = await profile_collection.find_one({"username": username})
                arg_type = "тегу"
        else:
            await response.edit_text(f'Ты ввёл что-то не то... попробуй задать <b>Xbox-ник</b> (<code>mynick</code>), <b>тег</b> (<code>@username</code>) или <b>ID аккаунта</b> (<code>1001101110</code>).')
        
        if profile_data:
            await profile(id = profile_data["_id"])

        else:
            await response.edit_text(f'По {arg_type} <b>{arg}</b> ничего не найдено.')

    else:
        await message.reply(f'<b>Укажи критерий</b> поиска после команды!\n\nЭто может быть <b>Xbox-ник</b> (<code>mynick</code>), <b>тег</b> (<code>@username</code>) или <b>ID аккаунта</b> (1001101110).')