import os
import random
import datetime
import time
import math

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from .keyboards import rice_kb, kb_close

load_dotenv()
bot_token = os.getenv('token')
cluster = AsyncIOMotorClient(os.getenv('db_link'))
chat_id = os.getenv('chat_id')
profile_collection = cluster.proj_one.profiles

bot = Bot(token = bot_token, parse_mode = "html")
dp = Dispatcher()

async def play(message: Message):
    player = await profile_collection.find_one({"_id": message.from_user.id})

    if player and "game" not in player:
        query = {"_id": player["_id"]}

        update = {
            "$set":
            {
                "game.played": "",
                "game.times_played": 0,
                "game.rice": 0,
            },
        }
        await profile_collection.update_one(query, update)

    if str(datetime.date.today()) != player.get("game", {}).get("played"):
        rep_count = player['rep'] // 30 # множитель рейта
        rice_count = player.get("game", {}).get("rice") # текущее кол-во
        rice_multiplier = rice_count // 100 # меньше риса за каждые 100 штук набранного

        if rice_count < 0:
            rice_multiplier = math.ceil(rice_multiplier) # округление в большую
        elif rice_count > 0:
            rice_multiplier = math.floor(rice_multiplier) # в меньшую

        if rice_multiplier > rep_count * 2:
            rice_multiplier = rep_count * 2


        if (player.get("game", {})).get("times_played") == 0:
            new_rice = int(random.randint(0, 8))
            if new_rice == 0:
                new_rice += 1
        else:
            new_rice = int(random.randint(-8, 10) + rep_count - rice_multiplier) # новый рис

        new_cg = 0
        if rice_count > 300 and (player.get("game", {})).get("catgirls") <= 5:
            chance = rice_count // 300
            if chance > 5:
                chance = 5
            rand = random.randint(1, 100)
            if rand <= chance:
                if new_rice >= 0:
                    new_cg = 1
                elif (player.get("game", {})).get("catgirls") > 0:
                    new_cg = -1



        query = {"_id": player["_id"]}

        update = {
            "$set":
            {
                "game.played": str(datetime.date.today())
            },
            "$inc":
            {
                "game.times_played": 1,
                "game.rice": new_rice,
                "game.catgirls": new_cg
            }
        }
        await profile_collection.update_one(query, update)


        add = ''
        if rice_count > 30:
            if rice_multiplier != 0:
                    add = f' (МК: {rice_multiplier})'
            if rep_count != 0:
                add = f' (СР: {rep_count})'
            if rep_count and rice_multiplier != 0:
                add = f' (МК: {rice_multiplier}, МР: {rep_count})'
                
                
        if new_rice < 0:
            if new_cg == 0:
                await message.reply(f'<b><a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a></b>, ты разочаровал партию! У тебя забрали {abs(new_rice)} 🍚{add} - теперь у тебя их {rice_count + new_rice}!\n\n<i>Возвращайся завтра!</i>')
            else:
                await message.reply(f'<b><a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a></b>, ты разочаровал партию! У тебя забрали {abs(new_rice)} 🍚{add} и 1 кошкожену - теперь у тебя {rice_count + new_rice} 🍚!\n\n<i>Возвращайся завтра!</i>')
            
        elif new_rice == 0:
            await message.reply(f'<b><a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>...</b> похоже, сегодня ты ничего не получишь. Ну, зато у тебя ничего не забрали!\n\n<i>Возвращайся завтра!</i>')
            
        elif new_rice > 0:
            if new_cg == 0:
                await message.reply(f'<b><a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a></b>, партия довольна тобой! Ты получаешь {new_rice} 🍚{add} - теперь у тебя их {rice_count + new_rice}!\n\n<i>Возвращайся завтра!</i>')
            else:
                await message.reply(f'<b><a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a></b>, партия довольна тобой! Ты получаешь {new_rice} 🍚{add} и 1 кошкожену - теперь у тебя {rice_count + new_rice} 🍚!\n\n<i>Возвращайся завтра!</i>')


    else:
        await message.reply(f'Сегодня <b>ты уже получил</b> награду/наказание от партии! Приходи завтра.')


async def pl_stats(message: Message):
    player = await profile_collection.find_one({"_id": message.from_user.id})

    if 'game' in player:
        rep_count = player['rep'] // 30 # множитель рейта
        rice_count = (player.get("game", {})).get("rice") # текущее кол-во
        rice_multiplier = rice_count // 100 # меньше риса за каждые 100 штук набранного
        times = (player.get("game", {})).get("times_played")

        if rice_count < 0:
            rice_multiplier = math.ceil(rice_multiplier) # округление в большую
        elif rice_count > 0:
            rice_multiplier = math.floor(rice_multiplier) # в меньшую

        if rice_multiplier > rep_count * 2:
            rice_multiplier = rep_count * 2
        
        await message.reply(f'<b>📊 Твоя статистика</b>\n\n<b>🍚 Всего мисок риса:</b> {rice_count}\n\n  - Множитель кол-ва: {rice_multiplier}\n  - Социальный рейтинг: {rep_count}\n\n<b>🎰 Всего сыграно раз:</b> {times}', reply_markup = rice_kb)
        
    else:
        await message.reply(f'<b>Ты ещё не получал ничего от партии!</b> Отправь команду /rice, чтобы начать игру.')


@dp.callback_query(lambda query: query.data == 'close')
async def delete_stats(call: CallbackQuery):
    if (await call.message.chat.get_member(call.from_user.id)).status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] or call.from_user.id == call.message.reply_to_message.from_user.id:
        await call.message.edit_text(f'<b>{call.from_user.full_name}</b> удалил сообщение.')
        time.sleep(3)
        await bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.answer('Статистику может закрыть только её владелец и админы.')


async def stats(message: Message):
    stats = '<b>📊 Статистика Партии</b>\n\n'
    count = 1

    players = profile_collection.find({"game": {"$exists": True}}).sort("game.rice", -1)
    async for player in players:
        if (player.get("game", {})).get("rice") != 0:
            stats += f'<b>{count}. {player["p_name"]}</b>: {(player.get("game", {})).get("rice")}\n'
            count += 1

    await message.reply(stats, reply_markup = kb_close)

@dp.callback_query(lambda query: query.data == 'delete')
async def delete_stats(call: CallbackQuery):
    if (await call.message.chat.get_member(call.from_user.id)).status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] or call.from_user.id == call.message.reply_to_message.from_user.id:
        await call.message.edit_text(f'<b>{call.from_user.full_name}</b> удалил сообщение.')
        time.sleep(3)
        await bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.answer('Статистику может закрыть только вызвавший её игрок и админы.')