import os
import keyboards
import datetime

from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from .states.states import RegisterState

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
bot_token = os.getenv('token')
chat_id = os.getenv('chat_id')
cluster = AsyncIOMotorClient(os.getenv('db_link'))
bot = Bot(token = bot_token, parse_mode = "html")
profile_collection = cluster.proj_one.profiles

async def edit_start(message: Message, state: FSMContext):
    if (await message.chat.get_member(message.from_user.id)).status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply('Ты не админ!')

    else:
        global profile, user
        if message.text == '/edit':
            if message.reply_to_message == None:
                await message.reply('<b>Ответь на сообщение</b> пользователя, профиль которого нужно изменить.')
            elif await profile_collection.find_one({"_id": message.reply_to_message.from_user.id}) == None:
                await message.reply('У этого пользователя нет профиля!')
            else:
                user = message.reply_to_message.from_user
                profile = await profile_collection.find_one({"_id": user.id})
                await message.reply(f'Выбери, что изменить в профиле игрока <b>{user.full_name}</b>.', reply_markup = keyboards.kb_edit)
                await state.set_state(RegisterState.edit_profile_state)
        else:
            arg = message.text.split(' ', 1)[1]

            if arg.isdigit():
                profile = await profile_collection.find_one({"_id": int(arg)})
                type = 'ID'
            elif not arg.isdigit():
                profile = await profile_collection.find_one({"nick": arg})
                type = 'ником'
                if profile == None:
                    username = arg.replace("@", "")
                    profile = await profile_collection.find_one({"username": username})
                    type = 'тегом'

            if profile == None:
                await message.reply(f'Профиля с {type} <b>{arg}</b> не существует.')
            elif message.reply_to_message != None: 
                user = message.reply_to_message.from_user
                await message.reply(f'Выбери, что изменить в профиле игрока <b>{user.full_name}</b>.', reply_markup = keyboards.kb_edit)
                await state.set_state(RegisterState.edit_profile_state)
            else:
                await message.reply(f'Выбери, что изменить в профиле игрока <b>{profile["p_name"]}</b>.', reply_markup = keyboards.kb_edit)
                await state.set_state(RegisterState.edit_profile_state)

async def edit_profile(message: Message, state: FSMContext):
    global msg, var, profile
    msg = message.text
    var = None
    if msg == "Имя":
        await message.reply(f"Введи новое <b>имя</b> для пользователя.")
        var = 'name'

    elif msg == "Ник":
        await message.reply(f"Введи новый <b>Xbox-ник</b> для пользователя.")
        var = 'nick'

    elif msg == "Возраст":
        await message.reply(f"Введи новый <b>возраст</b> для пользователя.")
        var = 'age'

    elif msg == "Пол":
        await message.reply(f"Введи новый <b>пол</b> для пользователя.")
        var = 's'

    elif msg == "Страна":
        await message.reply(f"Введи новую <b>страну</b> для пользователя.")
        var = 'country'

    elif msg == "Дата рождения":
        await message.reply(f"Введи новую <b>дату рождения</b> для пользователя <b>в формате 31.01.2001</b>")
        var = 'bd'

    elif msg == "Дата присоединения":
        await message.reply(f"Введи новую <b>дату присоединения</b> для пользователя <b>в формате 31.01.2001</b>")
        var = 'joined'

    elif msg == "Описание":
        await message.reply(f"Введи новое <b>описание</b> для пользователя.")
        var = 'bio'

    elif msg == "Удалить профиль":
        await message.reply(f"<b>Точно удалить профиль игрока {profile['p_name']}?</b>", reply_markup = keyboards.yes_no())
        var = 'delete'

    elif msg == 'Отмена':
        await message.reply(f'Редактирование профиля отменено.', reply_markup = ReplyKeyboardRemove())
        var = 'cancel'

    if var != None and var != 'bd' and var != 'joined' and var != 'delete' and var != 'cancel':
        await state.set_state(RegisterState.end_profile_state)
    elif var == 'bd':
        await state.set_state(RegisterState.edit_bd_state)
    elif var == 'joined':
        await state.set_state(RegisterState.edit_join_state)
    elif var == 'delete':
        await state.set_state(RegisterState.delete_profile_state)
    elif var == 'cancel':
        await state.clear()
    else:
        await message.reply(f'<b>Такого параметра нет!</b> Выбери один из вариантов на клавиатуре.')

async def edit_bd(message: Message, state: FSMContext):
    global profile
    bd_day = int(message.text[0:2])
    bd_month = int(message.text[3:5])
    bd_year = int(message.text[6:10])
    if bd_month > datetime.date.today().month:
        age = datetime.date.today().year - bd_year - 1
    elif bd_month == datetime.date.today().month:
        if bd_day > datetime.date.today().day:
            age = datetime.date.today().year - bd_year - 1
        elif bd_day < datetime.date.today().day:
            age = datetime.date.today().year - bd_year
        else:
            age = datetime.date.today().year - bd_year
    await state.update_data(regbd = message.text)
    new_bd = message.text

    await profile_collection.update_one({'_id': profile['_id']}, {'$set': {'bd': {"day": new_bd[0:2], "month": new_bd[3:5], "year": new_bd[6:10]}}})
    await profile_collection.update_one({'_id': profile['_id']}, {'$set': {'age': age}})

    await message.reply('Дата рождения изменена. Ты вернулся к редактированию профиля.\n\nВыбери "Отмена" для завершения.', reply_markup = keyboards.kb_edit)
    await state.set_state(RegisterState.edit_profile_state)

async def edit_join(message: Message, state: FSMContext):
    global profile
    new_j = message.text

    await profile_collection.update_one({'_id': profile['_id']}, {'$set': {'joined': {"day": new_j[0:2], "month": new_j[3:5], "year": new_j[6:10]}}})

    await message.reply('Дата присоединения изменена. Ты вернулся к редактированию профиля.\n\nВыбери "Отмена" для завершения.', reply_markup = keyboards.kb_edit)
    await state.set_state(RegisterState.edit_profile_state)

async def edit_end(message: Message, state: FSMContext):
    global profile
    await profile_collection.update_one({'_id': profile['_id']}, {'$set': {var: message.text}})
    await message.reply(f'Параметр "{msg}" изменён. Ты вернулся к редактированию профиля.\n\nВыбери "Отмена" для завершения.', reply_markup = keyboards.kb_edit)
    await state.set_state(RegisterState.edit_profile_state)

async def confirm_delete(message: Message, state: FSMContext):
    global profile
    if message.text.lower() == 'да':
        await profile_collection.delete_one({'_id': profile['_id']})
        await message.reply(f'<b>Профиль игрока удалён.</b> Редактирование завершено <i>(впрочем, редактировать уже нечего)</i>.', reply_markup = ReplyKeyboardRemove())
        await state.clear()
    elif message.text.lower() == 'нет':
        await message.reply(f'<b>Удаление профиля отменено.</b> Ты вернулся к его редактированию.\n\nВыбери "Отмена" для завершения.', reply_markup = keyboards.kb_edit)
        await state.set_state(RegisterState.edit_profile_state)