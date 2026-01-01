import os
import re

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId

from keyboards import kb_idea_rate, kb_idea_menu, kb_menu

load_dotenv()
bot_token = os.getenv('token')
cluster = AsyncIOMotorClient(os.getenv('db_link'))
chat_id = os.getenv('chat_id')
profile_collection = cluster.proj_one.profiles
ideas_collection = cluster.proj_one.ideas

bot = Bot(token = bot_token, parse_mode = "html")
dp = Dispatcher()

async def idea_suggest(message: Message):
    if len(message.text) > len('/s'):
        global idea
        idea = {
            "name": "Идея без имени",
            "sender": message.from_user.id,
            "sender_name": message.from_user.full_name,
            "idea_text": message.text.split(' ', 1)[1],
            "idea_full_text": "<b>Игрок <a href='tg://user?id=" + str(message.from_user.id) + "'>" + message.from_user.full_name + "</a> отправил идею:</b>\n\n<blockquote>" + message.text.split(' ', 1)[1] + "</blockquote>\n\n<b>ID:</b> " + str(message.from_user.id) + "\n<b>IID:</b>",
            "msg_id": 0,
            "rate": "none"
        } 
        idea_doc = await ideas_collection.insert_one(idea)


        idea_msg = await bot.send_message(-1002074241017, f"<b>Игрок <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a> отправил идею:</b>\n\n<blockquote>{message.text.split(' ', 1)[1]}</blockquote>\n\n<b>ID</b>: {message.from_user.id}\n<b>IID</b>: {idea_doc.inserted_id}", reply_markup = kb_menu, message_thread_id = 269)
        await ideas_collection.update_one({"_id": idea_doc.inserted_id}, {"$set": {"msg_id": idea_msg.message_id}})
        await message.reply(f'<b>Предложение отправлено</b> администрации сервера!')
    else:
        await message.reply(f'<b>Введи свою идею</b> для сервера, бота или т.п. после команды, чтобы отправить её.')



async def idea_menu(call: CallbackQuery):
    idea_text = call.message.text.split("\nID: ", 1)[0].split("\n", 1)[1]
    sender_id = call.message.text.split("\nID: ", 1)[1].split("\nIID: ", 1)[0]
    idea_id = call.message.text.split("\nIID: ", 1)[1]
    await call.message.edit_text(f'<blockquote>{idea_text}</blockquote><b>\nВыбери</b>, что сделать с этой идеей.\n\nID: {sender_id}\nIID: {idea_id}')
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = kb_idea_menu)



async def idea_rate(call: CallbackQuery):
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = kb_idea_rate)

async def idea_rename(call: CallbackQuery):
    await call.message.answer(f'<b>Ответь на сообщение</b> с идеей командой /rename <code>[имя]</code> <i>(это имя будет отображаться в списке идей)</i>.')

async def idea_renaming(message: Message):
    if message.reply_to_message != None:
        if len(message.text) > len('/rename'):
            await ideas_collection.update_one({"_id": ObjectId(message.reply_to_message.text.split("IID: ", 1)[1])}, {"$set": {"name": message.text.split(" ", 1)[1]}})
            await message.reply(f'<b>Идея переименована</b> в "{message.text.split(" ", 1)[1]}".')
        else:
            await message.reply(f'<b>Введи название идеи</b> после команды, чтобы переименовать её.')
    else:
        await message.reply(f'<b>Ответь на сообщение</b> с идеей, чтобы переименовать её.')

async def idea_cancel(call: CallbackQuery):
    idea_id = ObjectId(call.message.text.split("\nIID: ", 1)[1])
    idea_data = await ideas_collection.find_one({"_id": idea_id})
    await bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f'{idea_data["idea_full_text"]} {str(idea_data["_id"])}')
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = kb_menu)



async def idea_approve(call: CallbackQuery):
    pattern = r'ID:\s*(\d+)'
    match = re.search(pattern, call.message.text)
    if match:
        user_id = int(match.group(1))

    sender_profile = await profile_collection.find_one({"_id": user_id})
    query = {"_id": sender_profile["_id"]}
    update = {"$inc": {"rep": 10}}
    idea_data = await ideas_collection.find_one({"_id": ObjectId(call.message.text.split("\nIID: ", 1)[1])})
    await ideas_collection.update_one({"_id": ObjectId(call.message.text.split("\nIID: ", 1)[1])}, {"$set": {"rate": "approved"}})
    await profile_collection.update_one(query, update)
    await call.message.answer(f'Идея <b>одобрена и добавлена</b> в список полезных.\n\nИгрок <b>{sender_profile["nick"]}</b> был награждён репутацией <i>(+10)</i>.')
    await bot.send_message(user_id, f'Твоё предложение <b>было одобрено</b> админами! Тебе выдано <b>10 репутации</b>.\n\nТвоя идея: <blockquote>{idea_data["idea_text"]}</blockquote>')

async def idea_dismiss(call: CallbackQuery):
    pattern = r'id:\s*(\d+)'
    match = re.search(pattern, call.message.text)
    if match:
        user_id = int(match.group(1))

    idea_data = await ideas_collection.find_one({"_id": ObjectId(call.message.text.split("\nIID: ", 1)[1])})
    await ideas_collection.update_one({"_id": ObjectId(call.message.text.split("\nIID: ", 1)[1])}, {"$set": {"rate": "dismissed"}})
    await call.message.answer(f'Идея <b>отклонена</b>.')
    await bot.send_message(user_id, f'К сожалению, твоё предложение <b>было отклонено</b> админами.\n\nТвоя идея: <blockquote>{idea_data["idea_text"]}</blockquote>')

async def idea_punish(call: CallbackQuery):
    pattern = r'id:\s*(\d+)'
    match = re.search(pattern, call.message.text)
    if match:
        user_id = int(match.group(1))

    sender_profile = await profile_collection.find_one({"_id": user_id})
    query = {"_id": sender_profile["_id"]}
    update = {"$inc": {"rep": -10}}
    idea_data = await ideas_collection.find_one({"_id": ObjectId(call.message.text.split("\nIID: ", 1)[1])})
    await ideas_collection.update_one({"_id": ObjectId(call.message.text.split("\nIID: ", 1)[1])}, {"$set": {"rate": "punished"}})
    await profile_collection.update_one(query, update)
    await call.message.answer(f'Идея <b>отклонена</b>.\n\nРепутация игрока <b>{sender_profile["nick"]}</b> уменьшена <i>(-10)</i>.')
    await bot.send_message(user_id, f'Твоё предложение <b>было отклонено</b> админами. Твоя репутация <b>понижена на 10</b>.\n\nТвоя идея: <blockquote>{idea_data["idea_text"]}</blockquote>')

async def idea_rate_cancel(call: CallbackQuery):
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = kb_idea_menu)



async def idea_rate_send(call: CallbackQuery):
    source_idea = await ideas_collection.find_one({'_id': ObjectId(call.message.text.split('IID: ', 1)[1])})
    await call.message.answer(f'<b>Идея отправлена</b> в чат топиков на рассмотрение игрокам.')
    await bot.send_message(-1002038490886, f"<b>Идея от <a href='tg://user?id={source_idea['sender']}'>{source_idea['sender_name']}</a> была отправлена на рассмотрение игрокам:</b>\n\n<blockquote>{source_idea['idea_text']}</blockquote>\n\nОценивайте идею реакциями.", message_thread_id = 10)



async def approved_list(message: Message):
    approved_ideas = ''
    async for doc in ideas_collection.find({"rate": "approved"}):
        if len(doc["idea_text"]) > 50:
            idea_preview = doc["idea_text"][:50] + '...'
        else:
            idea_preview = doc["idea_text"]
        idea_data = f'<b>"<a href="https://t.me/c/2074241017/269/{doc["msg_id"]}">{doc["name"]}</a>"</b> от {doc["sender_name"]}.\n<blockquote>{idea_preview}</blockquote>\n\n'
        approved_ideas += idea_data
    await message.reply(f'<b>Список одобренных идей:</b>\n\n{approved_ideas}')