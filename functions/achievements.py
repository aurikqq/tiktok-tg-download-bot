import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from .states.states import RegisterState
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from .keyboards import kb_achs_back

load_dotenv()
bot_token = os.getenv('token')
cluster = AsyncIOMotorClient(os.getenv('db_link'))
chat_id = os.getenv('chat_id')
profile_collection = cluster.proj_one.profiles
ideas_collection = cluster.proj_one.ideas
achs_collection = cluster.proj_one.achievements

bot = Bot(token = bot_token, parse_mode = "html")
dp = Dispatcher()


async def start_adding(message: Message, state: FSMContext):
    if (await message.chat.get_member(message.from_user.id)).status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply('Ты не админ!')
    else:
        await message.reply(f"<b>Введи ID</b> для ачивки (например, break_the_host)")
        await state.set_state(RegisterState.ach_id_state)

async def set_id(message: Message, state: FSMContext):
    check = await achs_collection.find_one({'_id': message.text})
    if check == None:
        await message.reply(f"<b>ID сохранён</b> ({message.text}). Теперь <b>введи название</b> ачивки (например, Ботоломатель)")
        await state.update_data(id = message.text)
        await state.set_state(RegisterState.ach_name_state)
    else:
        await message.reply(f"Ачивка с таким ID уже существует.")
        await state.set_state(RegisterState.ach_name_state)

async def set_name(message: Message, state: FSMContext):
    await message.reply(f"<b>Название сохранено</b> ({message.text}). Осталось <b>ввести описание</b> ачивки - способ её получения.")
    await state.update_data(name = message.text)
    await state.set_state(RegisterState.ach_desc_state)
        
'''
async def set_desc(message: Message, state: FSMContext):
    await message.answer(f"<b>Описание сохранено</b> ({message.text}).")
    await state.update_data(regbd = message.text)
    await state.set_state(RegisterState.reg_s_state)
'''    
    	
async def save_ach(message: Message, state: FSMContext):
    await state.update_data(desc = message.text)
    ach_data = await state.get_data()
    ach_id = ach_data.get("id")
    ach_name = ach_data.get("name")
    ach_desc = ach_data.get("desc")

    ach_pattern = {
        '_id': '', 
        'name': '',
        'desc': ''
        }
    
    ach = ach_pattern.copy()
    ach.update({
        '_id': ach_id,
        'name': ach_name,
        'desc': ach_desc
        })
    
    achs_collection.insert_one(ach)

    await message.reply(f"Ачивка <b>{ach_name}</b> сохранена. Теперь её можно <b>добавить кому-нибудь в профиль</b> командой /ach")
    await state.clear()


async def give_ach(message: Message):
    if (await message.chat.get_member(message.from_user.id)).status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply('Ты не админ!')
    else:
        if message.text == '/ach':
            await message.reply('<b>Введи ID ачивки</b> для её выдачи кому-то. Список ачивок можно узнать через /ach_list')
        elif message.reply_to_message == None:
            await message.reply('<b>Ответь на сообщение</b> игрока, чтобы выдать ачивку.')
        else:
            id = message.text.split(' ', 1)[1]
            ach = await achs_collection.find_one({'_id': id})
            if not ach:
                await message.reply(f'Ачивки с ID <b>{id}</b> не существует!')
            else:
                player = await profile_collection.find_one({'_id': message.reply_to_message.from_user.id})
                if not player:
                    await message.reply(f'У пользователя <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b> нет профиля!')
                else:
                    if id in player['achs']:
                        await message.reply(f'Ачивка <b>{ach["name"]}</b> уже есть у игрока <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b>.')
                    else:
                        query = {"_id": player["_id"]}
                        update = {"$push": {"achs": id}}
                        await profile_collection.update_one(query, update)

                        await message.reply(f'Ачивка <b>{ach["name"]}</b> добавлена в профиль игрока <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b>.')


async def take_ach(message: Message):
    if (await message.chat.get_member(message.from_user.id)).status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply('Ты не админ!')
    else:
        if message.text == '/ach_take':
            await message.reply('<b>Введи ID ачивки</b>, чтобы убрать её у кого-то. Список ачивок можно узнать через /ach_list')
        elif message.reply_to_message == None:
            await message.reply('<b>Ответь на сообщение</b> игрока, чтобы убрать ачивку.')
        else:
            id = message.text.split(' ', 1)[1]
            ach = await achs_collection.find_one({'_id': id})
            if not ach:
                await message.reply(f'Ачивки с ID <b>{id}</b> не существует!')
            else:
                player = await profile_collection.find_one({'_id': message.reply_to_message.from_user.id})
                if not player:
                    await message.reply(f'У пользователя <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b> нет профиля!')
                else:
                    if id not in player['achs']:
                        await message.reply(f'У игрока <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b> нет ачивки <b>{ach["name"]}</b> (а ты её ещё и забрать пытаешься).')
                    else:
                        query = {"_id": player["_id"]}
                        update = {"$pull": {"achs": id}}
                        await profile_collection.update_one(query, update)

                        await message.reply(f'Ачивка <b>{ach["name"]}</b> убрана из профиля игрока <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b>.')


async def del_ach(message: Message):
    if (await message.chat.get_member(message.from_user.id)).status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply('Ты не админ!')
    else:
        if message.text == '/ach_del':
            await message.reply('<b>Введи ID ачивки</b>, чтобы удалить её. Список ачивок можно узнать через /ach_list')
        else:
            id = message.text.split(' ', 1)[1]
            ach = await achs_collection.find_one({'_id': id})
            if not ach:
                await message.reply(f'Ачивки с ID <b>{id}</b> не существует!')
            else:
                await achs_collection.delete_one({'_id': ach['_id']})
                await profile_collection.update_many({'achs': id}, {'$pull': {'achs': id}})

                await message.reply(f'Ачивка <b>{ach["name"]}</b> удалена и убрана из профилей.')


async def achs_list(message: Message):
    names = ''
    async for ach in achs_collection.find({}):
        name = ach['name']
        names += f'    - 🥇 {name}\n'
    list = f'<b>Достижения</b> могут быть созданы и выданы админами за заслуги перед сервером, в том числе шуточные.\n<b>Список достижений:</b>\n\n{names}\nЧтобы посмотреть описание какого-то из них, <b>ответь на это сообщение</b> командой <code>/ach_help [название]</code>, например <code>/ach_help Хостолом</code>.'
    await message.reply(list)

async def ach_help(message: Message):
    if '/ach_help' in message.reply_to_message.text:
        if '/ach_help' in message.text:
            name = message.text.split(' ', 1)[1]
            ach = await achs_collection.find_one({'name': name})
            if not ach:
                await message.reply(f'Достижения с именем <b>{name}</b> не существует!')
            else:
                text = f'🥇 <b>Достижение "{name}"</b>\n\n<b>ID:</b> {ach["_id"]}\n\n<b>Описание:</b> {ach["desc"]}'
                await message.reply_to_message.edit_text(text, reply_markup = kb_achs_back)

async def ach_back(call: CallbackQuery):
    names = ''
    async for ach in achs_collection.find({}):
        name = ach['name']
        names += f'    - 🥇 {name}\n'
    list = f'<b>Достижения</b> могут быть созданы и выданы админами за заслуги перед сервером, в том числе шуточные.\n<b>Список достижений:</b>\n\n{names}\nЧтобы посмотреть описание какого-то из них, <b>ответь на это сообщение</b> командой <code>/ach_help [название]</code>, например <code>/ach_help Хостолом</code>.'
    await call.message.edit_text(list)
    await call.message.delete_reply_markup()
