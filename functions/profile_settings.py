import os

from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from .profile import p_1

load_dotenv()
bot_token = os.getenv('token')
cluster = AsyncIOMotorClient(os.getenv('db_link'))
chat_id = os.getenv('chat_id')
profile_collection = cluster.proj_one.profiles

bot = Bot(token = bot_token, parse_mode = "html")
dp = Dispatcher()


async def profile_settings(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        profile_settings = InlineKeyboardBuilder()

        profile_settings.button(text = "Скрыть данные", callback_data = "hide_data")
        profile_settings.button(text = "Дополнить профиль", callback_data = "add_data")
        profile_settings.button(text = "Удалить профиль", callback_data = "delete_profile")
        profile_settings.button(text = "‹ Назад", callback_data = f"ps_back:{call.from_user.id}")

        profile_settings.adjust(1)

        await call.message.edit_text("<b>Настройки профиля</b>\n\nЗдесь ты можешь скрыть часть личных данных из своего профиля, добавить новые или удалить профиль.", reply_markup = profile_settings.as_markup())
    else:
        await call.answer('Это не для тебя.')


async def hide_data(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        player = await profile_collection.find_one({"_id": call.from_user.id})

        set_hidden_data = InlineKeyboardBuilder()

        if player.get("hidden", {}).get("name"):
            set_hidden_data.button(text = "Имя ❌", callback_data = "hide_name")
        else:
            set_hidden_data.button(text = "Имя ✅", callback_data = "hide_name")

        if player.get("hidden", {}).get("age"):
            set_hidden_data.button(text = "Возраст ❌", callback_data = "hide_age")
        else:
            set_hidden_data.button(text = "Возраст ✅", callback_data = "hide_age")

        if player.get("hidden", {}).get("country"):
            set_hidden_data.button(text = "Страна ❌", callback_data = "hide_country")
        else:
            set_hidden_data.button(text = "Страна ✅", callback_data = "hide_country")

        set_hidden_data.button(text = "‹ Назад", callback_data = "back_to_ps")

        set_hidden_data.adjust(2)

        await call.message.edit_text("<b>Что именно ты хочешь скрыть?</b>\n\nУже скрытые параметры помечены крестом (❌), активные - знаком ✅.", reply_markup = set_hidden_data.as_markup())
    else:
        await call.answer('Это не для тебя.')

async def hide_name(call: CallbackQuery):
    player = await profile_collection.find_one({"_id": call.from_user.id})

    query = {"_id": player["_id"]}
    update = {"$set": {"hidden.name": True if not player["hidden"]["name"] else False}}
    await profile_collection.update_one(query, update)
    await hide_data(call)

async def hide_age(call: CallbackQuery):
    player = await profile_collection.find_one({"_id": call.from_user.id})

    query = {"_id": player["_id"]}
    update = {"$set": {"hidden.age": True if not player["hidden"]["age"] else False}}
    await profile_collection.update_one(query, update)
    await hide_data(call)

async def hide_country(call: CallbackQuery):
    player = await profile_collection.find_one({"_id": call.from_user.id})

    query = {"_id": player["_id"]}
    update = {"$set": {"hidden.country": True if not player["hidden"]["country"] else False}}
    await profile_collection.update_one(query, update)
    await hide_data(call)


async def add_data(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        player = await profile_collection.find_one({"_id": call.from_user.id})

        add_new_data = InlineKeyboardBuilder()
        if player["bio"] == "отсутствует":
            add_new_data.button(text = "Добавить \"О себе\"", callback_data = "add_bio")
        else:
            add_new_data.button(text = "Убрать \"О себе\"", callback_data = "remove_bio")

        if player["pic"] == "":
            add_new_data.button(text = "Дбоавить фото", callback_data = "add_pic")
        else:
            add_new_data.button(text = "Убрать фото", callback_data = "remove_pic")

        if player["edition"] == "-":
            add_new_data.button(text = "Добавить издание", callback_data = "add_edition")
        else:
            add_new_data.button(text = "Убрать издание", callback_data = "remove_edition")
            
        add_new_data.button(text = "‹ Назад", callback_data = "back_to_ps")

        add_new_data.adjust(2, 2)

        await call.message.edit_text("Ты можешь добавить в свой профиль разные необязательные данные, если у тебя ещё нет их, или убрать их. <b>Выбери нужный пункт</b>, и следуй инструкциям.", reply_markup = add_new_data.as_markup())
        
    else:
        await call.answer('Это не для тебя.')

async def add_bio(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        back_to_add_data = InlineKeyboardBuilder()
        back_to_add_data.button(text = "‹ Назад", callback_data = "back_to_add_data")
        await call.message.edit_text("Чтобы изменить раздел \"О себе\", <b>отправь команду</b> <code>/bio [текст]</code>. Описание должно быть не длиннее 150-и символов.", reply_markup = back_to_add_data.as_markup())
    else:
        await call.answer('Это не для тебя.')

async def add_pic(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        back_to_add_data = InlineKeyboardBuilder()
        back_to_add_data.button(text = "‹ Назад", callback_data = "back_to_add_data")
        await call.message.edit_text("Чтобы установить фото в профиль, прочти <a href='https://telegra.ph/Kak-ustanovit-foto-profilya-v-bote-03-09'>эту статью</a>.", reply_markup = back_to_add_data.as_markup())
    else:
        await call.answer('Это не для тебя.')

async def add_edition(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        back_to_add_data = InlineKeyboardBuilder()
        back_to_add_data.button(text = "‹ Назад", callback_data = "back_to_add_data")
        await call.message.edit_text("Чтобы указать, на каком издании Майнкрафта ты играешь (Java, Bedrock или оба), <b>отправь команду</b> <code>/edition</code>.", reply_markup = back_to_add_data.as_markup())
    else:
        await call.answer('Это не для тебя.')

async def remove_bio(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        back_to_add_data = InlineKeyboardBuilder()
        back_to_add_data.button(text = "‹ Назад", callback_data = "back_to_add_data")
        await profile_collection.update_one({"_id": call.from_user.id}, {"$set": {"bio": "отсутствует"}})
        
        await call.message.edit_text("Раздел \"О себе\" удалён из твоего профиля.", reply_markup = back_to_add_data.as_markup())
    else:
        await call.answer('Это не для тебя.')

async def remove_pic(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        back_to_add_data = InlineKeyboardBuilder()
        back_to_add_data.button(text = "‹ Назад", callback_data = "back_to_add_data")
        await profile_collection.update_one({"_id": call.from_user.id}, {"$set": {"pic": ""}})
        
        await call.message.edit_text("Фото профиля удалено.", reply_markup = back_to_add_data.as_markup())
    else:
        await call.answer('Это не для тебя.')

async def remove_edition(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        back_to_add_data = InlineKeyboardBuilder()
        back_to_add_data.button(text = "‹ Назад", callback_data = "back_to_add_data")
        await profile_collection.update_one({"_id": call.from_user.id}, {"$set": {"edition": "-"}})
        
        await call.message.edit_text("Издание игры удалено из профиля.", reply_markup = back_to_add_data.as_markup())
    else:
        await call.answer('Это не для тебя.')

async def delete_profile(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        sure_to_delete = InlineKeyboardBuilder()
        sure_to_delete.button(text = "Да", callback_data = "delete_yes")
        sure_to_delete.button(text = "Нет", callback_data = "back_to_ps")
        await call.message.edit_text("<b>Точно хочешь удалить свой профиль?</b>", reply_markup = sure_to_delete.as_markup())
    else:
        await call.answer('Это не для тебя.')

async def delete_yes(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        await profile_collection.delete_one({"_id": call.from_user.id})
        await call.message.edit_text("Твой профиль удалён.")
    else:
        await call.answer('Это не для тебя.')


async def back_to_profile(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        await p_1(call, True)
    else:
        await call.answer('Это не для тебя.')