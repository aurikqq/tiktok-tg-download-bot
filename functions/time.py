import os
import time
import pytz

from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from keyboards import kb_countries_1, kb_countries_2, kb_country

load_dotenv()
bot_token = os.getenv('token')
cluster = AsyncIOMotorClient(os.getenv('db_link'))
chat_id = os.getenv('chat_id')
profile_collection = cluster.proj_one.profiles

bot = Bot(token = bot_token, parse_mode = "html")
dp = Dispatcher()

async def time_menu(message: Message):
    await message.reply(f'<b>Выбери нужную страну</b>, чтобы узнать время в ней.', reply_markup = kb_countries_1)

async def country_1(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup = kb_countries_1)

async def country_2(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup = kb_countries_2)

async def back(call: CallbackQuery):
    await call.message.reply(f'<b>Выбери нужную страну</b>, чтобы узнать время в ней.', reply_markup = kb_countries_1)
    await call.message.edit_reply_markup(reply_markup = kb_countries_1)

async def close(call: CallbackQuery):
    await call.message.edit_text(f'<b>{call.from_user.full_name}</b> удалил сообщение.')
    time.sleep(3)
    await bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
    await call.message.delete()

async def country(call: CallbackQuery):
    if call.data == 'RU':
        word = 'России'
        country = 'Россия'
    if call.data == 'BY':
        word = 'Беларуси'
        country = 'Беларусь'
    elif call.data == 'SE':
        word = 'Швеции'
        country = 'Швеция'
    elif call.data == 'AZ':
        word = 'Азербайджане'
        country = 'Азербайджан'
    elif call.data == 'KZ':
        word = 'Казахстане'
        country = 'Казахстан'
    elif call.data == 'UA':
        word = 'Украине'
        country = 'Украина'
    elif call.data == 'UZ':
        word = 'Узбекистане'
        country = 'Узбекистан'
    elif call.data == 'DE':
        word = 'Германии'
        country = 'Германия'

    timezone = pytz.country_timezones[call.data][0]
    current_time = datetime.now(pytz.timezone(timezone))
    time = current_time.strftime('%m.%d, %H:%M')

    await call.message.edit_text(f'<b>Время в {word}:</b> {time}.\nВ чате <b>{await profile_collection.count_documents({"country": country})}</b> игрок(а) из этой страны.')
    await call.message.edit_reply_markup(reply_markup = kb_country)