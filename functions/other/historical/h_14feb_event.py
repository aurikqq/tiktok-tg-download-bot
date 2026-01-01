import os, time, datetime

from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from keyboards import valentine_take

load_dotenv()
bot_token = os.getenv('token')
cluster = AsyncIOMotorClient(os.getenv('db_link'))
chat_id = os.getenv('chat_id')
profile_collection = cluster.proj_one.profiles

bot = Bot(token = bot_token, parse_mode = "html")
dp = Dispatcher()

async def send_valentine():
    current_time = datetime.datetime.now()
    if current_time.month == 2 and current_time.day == 14:
        await bot.send_message(chat_id, '💌', reply_markup = valentine_take)

async def take_val(call: CallbackQuery):
    taked_user = await profile_collection.find_one({"_id": call.from_user.id})
    await profile_collection.update_one({'_id': call.from_user.id}, {'$inc': {'valentines': 1}})
    await bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f'<b><a href="tg://user?id={call.from_user.id}">{call.from_user.full_name}</a></b> забрал валентинку! Теперь у игрока их <b>{taked_user["valentines"] + 1}</b>')
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = None)
    time.sleep(600)
    await bot.delete_message(chat_id, call.message.message_id)