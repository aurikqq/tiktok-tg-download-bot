import os
import datetime

from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from .states.states import RegisterState
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
bot_token = os.getenv('token')
bot = Bot(token=bot_token, parse_mode="html")
cluster = AsyncIOMotorClient(os.getenv('db_link'))
profile_collection = cluster.proj_one.profiles


async def start_reg(message: Message, state: FSMContext):
    database = await profile_collection.find_one({'_id': message.from_user.id})
    if database == None:
        await message.answer(
            f"Для начала, введи своё <b>настоящее имя</b>.\n\nРегистрация проводится только один раз, и впоследствии ты не сможешь изменить введенные данные.")
        await state.set_state(RegisterState.reg_name_state)
    else:
        await message.answer(f"Ты уже зарегистрирован! <b>Введи !профиль,</b> чтобы посмотреть свои данные.")
        await state.clear()


async def save_name(message: Message, state: FSMContext):
    await message.answer(
        f"Имя сохранено ({message.text}).\n\nТеперь укажи <b>свой ник</b> в игре.")
    await state.update_data(regname=message.text)
    await state.set_state(RegisterState.reg_nick_state)


async def save_nick(message: Message, state: FSMContext):
    await message.answer(
        f"Ник сохранен ({message.text}).\n\nТеперь введи свою <b>дату рождения</b> в формате 31.01.2001")
    await state.update_data(regnick=message.text)
    await state.set_state(RegisterState.reg_bd_state)


async def save_bd(message: Message, state: FSMContext):
    if len(message.text) == 10 and message.text[2] == '.' and message.text[5] == '.':
        global reg_bd_day
        global reg_bd_month
        global reg_bd_year
        global age
        global is_bd_today
        is_bd_today = False
        reg_bd_day = int(message.text[0:2])
        reg_bd_month = int(message.text[3:5])
        reg_bd_year = int(message.text[6:10])
        if reg_bd_month > datetime.date.today().month:
            age = datetime.date.today().year - reg_bd_year - 1
        elif reg_bd_month == datetime.date.today().month:
            if reg_bd_day > datetime.date.today().day:
                age = datetime.date.today().year - reg_bd_year - 1
            elif reg_bd_day < datetime.date.today().day:
                age = datetime.date.today().year - reg_bd_year
            else:
                age = datetime.date.today().year - reg_bd_year
                is_bd_today = True
        else:
            age = datetime.date.today().year - reg_bd_year

        if is_bd_today == True:
            await message.answer(
                f"Дата рождения сохранена ({message.text}, {age} лет). С днём рождения, {message.from_user.full_name}!\n\nПродолжаем. Теперь введи <b>свой пол.</b> Принимаются только мужской или женский.")
        else:
            await message.answer(
                f"Дата рождения сохранена ({message.text}, {age} лет).\n\nТеперь введи <b>свой пол.</b> Принимаются только мужской или женский.")

        await state.update_data(regbd = message.text)
        await state.set_state(RegisterState.reg_s_state)
    else:
        await message.answer(f"Дата введена неверно. Правильный пример указан в сообщении выше.")


async def save_s(message: Message, state: FSMContext):
    if message.text.lower() == "мужской" or message.text.lower() == "женский":
        await message.answer(
            f"Пол сохранен ({message.text}).\n\nПоследний вопрос – укажи <b>страну</b>, в которой ты живешь.")
        await state.update_data(regs=message.text.lower())
        await state.set_state(RegisterState.reg_country_state)
    else:
        await message.answer(f"Пол введен неверно. Укажи <b>мужской</b> или <b>женский.</b>")


async def save_country(message: Message, state: FSMContext):
    await state.update_data(regcountry = message.text)
    reg_data = await state.get_data()
    reg_name = reg_data.get("regname")
    reg_nick = reg_data.get("regnick")
    reg_bd = reg_data.get("regbd")
    reg_s = reg_data.get("regs")
    reg_country = reg_data.get("regcountry")

    global j_day, j_month
    if datetime.date.today().day < 10:
        j_day = "0" + str(datetime.date.today().day)
    else:
        j_day = str(datetime.date.today().day)
    if datetime.date.today().month < 10:
        j_month = "0" + str(datetime.date.today().month)
    else:
        j_month = str(datetime.date.today().month)

    profile = {
        "_id": message.from_user.id,
        "name": reg_name,
        "nick": reg_nick,
        "age": age,
        "bd": {
            "day": reg_bd[0:2],
            "month": reg_bd[3:5],
            "year": reg_bd[6:10]
        },
        "s": reg_s,
        "rep": 0,
        "bio": "отсутствует",
        "country": reg_country,
        "joined": {
            "day": j_day,
            "month": j_month,
            "year": str(datetime.date.today().year)
        },
        "pic": '',
        "last_game": '-',
        "edition": '',
        "city": '',
        "achs": [],
        "game": {},
        "p_name": message.from_user.full_name,
        "username": message.from_user.username,
        "hidden": {
            "name": False,
            "age": False,
            "country": False
        },
    }

    profile_collection.insert_one(profile)

    await bot.send_message(1104899353,
                           f"Кто-то зарегистрировался.\n\nИмя: {message.from_user.full_name}\nАйди: {message.from_user.id}\nЮзернейм: @{message.from_user.username}")
    await state.clear()
    await message.answer(
                f"Страна сохранена ({message.text}).\n\n<b>Регистрация завершена</b>. Ты можешь посмотреть свой профиль командой <b>!п</b>, а также указать издание Майнкрафта, на котором ты играешь, командой <b>/edition</b>")

