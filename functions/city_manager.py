import os
import re

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from .states.states import RegisterState
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

import keyboards

load_dotenv()
bot_token = os.getenv('token')
chat_id = os.getenv('chat_id')

bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode = 'html'))
dp = Dispatcher()

cluster = AsyncIOMotorClient(os.getenv('db_link'))
profile_collection = cluster.proj_one.profiles
city_collection = cluster.proj_one.cities
data_collection = cluster.proj_one.data


async def city_preadd(message: Message):
    player = await profile_collection.find_one({'_id': message.from_user.id})
    if player:
        city_check = await city_collection.find_one({'owner': player['nick']})
        if city_check:
            await message.reply("У тебя уже есть свой город!")
        elif player['rep'] < 10:
            await message.reply('Тебе нужно набрать 10 репутации для основания города.')
        else:
            await message.reply('Перед тем, как добавить в бота информацию о своём городе, прочти <a href="https://telegra.ph/Pravila-osnovaniya-gorodov-06-16"><b>правила его основания</b></a> <i>(в них также есть пример регистрации города)</i>\n\nЧтобы начать, <b>нажми на кнопку</b> снизу. Если кто-то уже добавляет свой город, дождись окончания и начинай.', reply_markup = keyboards.kb_city_continiue, disable_web_page_preview = True)
    else:
        await message.reply("У тебя нет профиля. <b>Отправь /r</b>, чтобы создать его")

async def city_add(call: CallbackQuery, state: FSMContext):
    global bot_msg, city
    bot_msg = call.message
    if call.from_user == bot_msg.reply_to_message.from_user:
        city = ({})
        await bot_msg.edit_text(f'<b>Хорошо, тогда начнём.</b>\nКак называется город?\n\nЕсли ты ошибёшься в чём-то, сможешь исправить данные в конце.')
        await state.set_state(RegisterState.city_name_state)
    else:
        await call.answer('Это не для тебя!')

async def city_count(message: Message, state: FSMContext):
    check = await city_collection.find_one({'name': message.text})
    if check == None:
        await message.reply(f'<b>Понял, продолжим.</b>\nПеречисли через запятую ники горожан - например, player1, player2, player3...')
        city['name'] = message.text
        global city_name
        city_name = message.text
        await state.set_state(RegisterState.city_citizens_state)
    else:
        owner = await profile_collection.find_one({'nick': check['owner']})
        await message.reply(f"Город с таким названием уже существует, его глава - <b><a href='tg://user?id={owner['_id']}'>{owner['p_name']}</a></b>.")

async def city_citizens(message: Message, state: FSMContext):
    citizens = message.text.split(', ')
    min_count = await data_collection.find_one({'_id': 'city_min_count'})
    if len(citizens) >= int(min_count['value']):
        pattern = r'^\s*[\w\s]+(?:,\s*[\w\s]+)*\s*$'
        if re.match(pattern, message.text):
            await message.reply('<b>Отлично, мы почти закончили.</b>\nПоследнее, что тебе нужно указать - на каких координатах находится твой город?\n\nЖелательно указать координаты его центра в виде <b>x ~ z</b> - например, <b>1000 ~ -150</b>.')
            city['citizens'] = citizens
            city['count'] = len(citizens)
            global city_citizens_raw
            city_citizens_raw = message.text
            await state.set_state(RegisterState.city_coords_state)
        else:
            await message.reply('Введи ники жителей города <b>через запятую</b> - например, player1, player2, player3 и т.д.')
    else:
        await message.reply(f'В городе должно быть <b>минимум {min_count["value"]}</b> жителей! Теперь жди бана, раз не прочёл <a href="https://telegra.ph/Pravila-osnovaniya-gorodov-06-16">правила</a> <i>(ну или вводи список ещё раз, если ошибся)</i>.', reply_markup = keyboards.kb_city_cancel, disable_web_page_preview = True)
        
async def city_coords(message: Message, state: FSMContext):
    pattern = r'^-?\d+\s*~\s*-?\d+$'
    if re.match(pattern, message.text):
        owner = await profile_collection.find_one({'_id': message.from_user.id})
        city['owner'] = owner['nick']
        city['coords'] = message.text
        await message.reply(f"<b>Итак, сверим данные.</b>\n\nГород <b>{city['name']}</b> игрока <a href='tg://user?id={message.from_user.id}'><b>{message.from_user.full_name}</b></a>\n<b>Население:</b> {city['count']}\n<b>Горожане:</b> {city_citizens_raw}\n<b>Координаты:</b> {city['coords']}\n\nВсё верно или что-то нужно изменить?", reply_markup = keyboards.kb_city_confirm)
        await state.clear()
    else:
        await message.reply('Введи координаты города <b>как в игре</b> - например, <b>1200 ~ -150</b>.')

async def save_city(call: CallbackQuery):
    if bot_msg.reply_to_message.from_user == call.from_user:
        for citizen in city['citizens']:
            player = await profile_collection.find_one({'nick': citizen})
            if player:
                query = {"_id": player["_id"]}
                update = {"$set": {"city": city['name']}}
                await profile_collection.update_one(query, update)
            else:
                await call.message.answer(f"Игрока с ником <b>{citizen} не существует.")
                missing_player = True

        if missing_player:
            city_collection.insert_one(city)
            await call.message.edit_text(f"<b>Готово!</b> Город <b>{city['name']}</b> добавлен в список городов и профили всех его жителей.\n\nТы можешь изменить данные или добавить фото/описание города командой /edit_city.")


async def city_back(call: CallbackQuery, state: FSMContext):
    if call.from_user == call.message.reply_to_message.from_user:
        await call.message.edit_text(f"<b>Итак, сверим данные.</b>\n\nГород <b>{city['name']}</b> игрока <a href='tg://user?id={call.from_user.id}'><b>{call.from_user.full_name}</b></a>\n<b>Население:</b> {city['count']}\n<b>Горожане:</b> {city_citizens_raw}\n<b>Координаты:</b> {city['coords']}\n\nВсё верно или что-то нужно изменить?", reply_markup = keyboards.kb_city_confirm)
        await state.clear()
    else:
        await call.answer('Это не для тебя!')



async def edit_city(call: CallbackQuery):
    await call.message.edit_text('Что требуется изменить?', reply_markup = keyboards.kb_city_edit)

async def city_edit_name(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"<b>Введи новое имя</b> для города. Прошлое: <b>{city['name']}</b>.", reply_markup = keyboards.kb_city_edit_back)
    await state.set_state(RegisterState.city_name_edit_state)

async def city_edited_name(message: Message, state: FSMContext):
    check = await city_collection.find_one({'name': message.text})
    if check == None:
        await message.reply(f'Имя изменено на <b>{message.text}</b>. Ещё что-то?', reply_markup = keyboards.kb_city_edit)
        city['name'] = message.text
    else:
        owner = await profile_collection.find_one({'nick': check['owner']})
        await message.reply(f"Город с таким названием уже существует, его глава - <b><a href='tg://user?id={owner['_id']}'>{owner['p_name']}</a></b>.")


async def city_edit_citizens(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f'<b>Введи новый список жителей</b> для города. Прошлый: <b>{city_citizens_raw}</b>.', reply_markup = keyboards.kb_city_edit_back)
    await state.set_state(RegisterState.city_citizens_edit_state)

async def city_edited_citizens(message: Message, state: FSMContext):
    citizens = message.text.split(', ')
    min_count = await data_collection.find_one({'_id': 'city_min_count'})
    if len(citizens) >= int(min_count['value']):
        pattern = r'^\s*[\w\s]+(?:,\s*[\w\s]+)*\s*$'
        if re.match(pattern, message.text):
            await message.reply(f'<b>Список горожан изменён</b> ({message.text} - {len(citizens)} чел.). Ещё что-то?', reply_markup = keyboards.kb_city_edit)
            city['citizens'] = citizens
            city['count'] = len(citizens)
            global city_citizens_raw
            city_citizens_raw = message.text
        else:
            await message.reply('Введи ники жителей города <b>через запятую</b> - например, player1, player2, player3 и т.д.')
    else:
        await message.reply(f'В городе должно быть <b>минимум {min_count["value"]}</b> жителей. Введи список ещё раз, если ошибся.', reply_markup = keyboards.kb_city_cancel)


async def city_edit_coords(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"<b>Введи новые координаты</b> для города. Прошлые: <b>{city['coords']}</b>.", reply_markup = keyboards.kb_city_edit_back)
    await state.set_state(RegisterState.city_coords_edit_state)

async def city_edited_coords(message: Message, state: FSMContext):
    pattern = r'^-?\d+\s*~\s*-?\d+$'
    if re.match(pattern, message.text):
        city['coords'] = message.text
        await message.reply(f'Координаты изменены на <b>{message.text}</b>. Ещё что-то?', reply_markup = keyboards.kb_city_edit)
    else:
        await message.reply('Введи координаты города <b>как в игре</b> - например, <b>1200 ~ -150</b>.')


async def city_add_cancel(call: CallbackQuery):
    if call.message.reply_to_message.from_user == call.from_user:
        await call.message.edit_text('Добавление города отменено.')
    else:
        await call.answer('Это не для тебя!')
    


async def about_city(message: Message):
    if message.text == '/city':
        await message.reply('Укажи <b>название города</b> после команды.')
    else:
        city_name = message.text.split(' ', 1)[1]
        city = await city_collection.find_one({'name': city_name})
        if city:
            if str(city['count'])[-1] == '1':
                citizens = f'<b>{city["count"]} житель:</b>\n'
            elif str(city['count'])[-1] in ['0', '2', '3', '4']:
                citizens = f'<b>{city["count"]} жителя:</b>\n'
            else:
                citizens = f'<b>{city["count"]} жителей:</b>\n'

            for citizen in city['citizens']:
                citizens += f'    - {citizen}\n'

            if "about" in city:
                about = f"<b>О городе:</b> {city['about']}\n\n"
            else:
                about = ""
            if "pic" in city:
                photo_id = city["pic"]
                await message.reply_photo(photo = photo_id, caption = f'<b>Город {city["name"]} игрока {city["owner"]}</b>\n\n{citizens}\n{about}<b>Расположение:</b> {city["coords"]}')
            else:
                await message.reply(f'<b>Город {city["name"]} игрока {city["owner"]}</b>\n\n{citizens}\n{about}<b>Расположение:</b> {city["coords"]}')

        else:
            await message.reply(f'Города <b>{city_name}</b> не существует!')


async def delete_city(message: Message):
        player = await profile_collection.find_one({'_id': message.from_user.id})
        if message.text == '/city_delete':
            if (await message.chat.get_member(message.from_user.id)).status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                city = await city_collection.find_one({"owner": player["nick"]})
                if city:
                    await message.reply(f"Твой город <b>{city['name']}</b> удалён и убран из профилей.")
                else:
                    await message.reply('У тебя нет города.')
            else:
                await message.reply('<b>Введи название города</b>, чтобы удалить его. Список городов можно узнать через /city_list')
        else:
            city_name = message.text.split(' ', 1)[1]
            city = await city_collection.find_one({'name': city_name})
            if city and player:
                if (await message.chat.get_member(message.from_user.id)).status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] and city['owner'] != player['nick']:
                    await message.reply('Удалить город могут только админы и глава этого города.')
                else:
                    city = await city_collection.find_one({'name': city_name})
                    if not city:
                        await message.reply(f'Города <b>{city_name}</b> не существует!')
                    else:
                        await city_collection.delete_one({'name': city['name']})
                        await profile_collection.update_many({'city': city_name}, {'$unset': {'city': ''}})

                        await message.reply(f'Город <b>{city["name"]}</b> удалён и убран из профилей.')
            elif not city:
                await message.reply(f'Города <b>{city_name}</b> не существует.')
            elif not player:
                await message.reply(f'У тебя нет профиля. <b>Отправь /r</b>, чтобы создать его')


async def cities_list(message: Message):
    names = ''
    list_count = 1
    cities = []

    for city in await city_collection.find({}).to_list(length = 50):
        cities.append(city)

    counts = [int(city['count']) for city in cities]
    counts.sort()

    for city in cities:
        name = city['name']
        count = city['count']
        owner = city['owner']
        owner_data = await profile_collection.find_one({'nick': owner})

        if str(count)[-1] == '1':
            citizens = f'{count} житель'
        elif str(count)[-1] in ['0', '2', '3', '4']:
            citizens = f'{count} жителя'
        else:
            citizens = f'{count} жителей'

        names += f'<b>{list_count}. {name}</b>\n    - {citizens}, глава: <a href="tg://user?id={owner_data["_id"]}">{owner_data["p_name"]}</a>.\n\n'
        list_count += 1
        
    list = f'<b>Города на сервере:</b>\n\n{names}Чтобы посмотреть подробности о городе, <b>отправь команду</b> <code>/city [название]</code>.'
    await message.reply(list)

async def edit_city(message: Message):
    player = await profile_collection.find_one({'_id': message.from_user.id})
    city = await city_collection.find_one({"owner": player["nick"]})
    if (await message.chat.get_member(message.from_user.id)).status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] or city:
        if message.text == "/city_edit":
            await message.reply("Укажи параметр, который нужно изменить, и его новое значение (например, /city_edit name Новое имя)\n\nДоступные параметры:\n  - name - название\n  - players - горожане\n  - coords - координаты\n  - about - описание\n  - pic - фото (отправь как подпись к фото)")
            
        
        if not message.photo:
            if message.text.count(' ') == 1:
                await message.reply(f"Добавь к команде новое значение для параметра <b>{message.text.split(' ')[1]}</b>.")
            
            else:
                arg = message.text.split(' ', 1)[1].split(' ', 1)[0]
                value = message.text.split(' ', 2)[2]

                if arg == 'name':
                    await city_collection.update_one({"owner": player["nick"]}, {"$set": {"name": value}})
                    await message.reply(f'Название изменено на <b>{value}</b>.')

                elif arg == 'players':
                    citizens = value.split(', ')
                    min_count = await data_collection.find_one({'_id': 'city_min_count'})
                    if len(citizens) >= int(min_count['value']):
                        pattern = r'^\s*[\w\s]+(?:,\s*[\w\s]+)*\s*$'
                        if re.match(pattern, value):
                            await message.reply(f"Список горожан изменён на <b>{value}</b>.")
                            city_collection.update_one({"owner": player["nick"]}, {"$set": {"citizens": citizens, "count": len(citizens)}})
                        else:
                            await message.reply("Введи новый список горожан через запятую.")
                    else:
                        await message.reply(f"В городе должно быть <b>минимум {min_count['value']}</b> жителей.")

                elif arg == 'coords':
                    pattern = r'^-?\d+\s*~\s*-?\d+$'
                    if re.match(pattern, message.text):
                        await city_collection.update_one({"owner": player["nick"]}, {"$set": {"coords": value}})
                        await message.reply(f"Расположение города изменено на <b>{value}</b>.")
                    else:
                        await message.reply("Введи новое расположение города <b>как в игре</b> - например, <b>1200 ~ -150</b>.")

                elif arg == "about":
                    if len(value) > 30:
                        value = value[:30] * "..."
                    await city_collection.update_one({"owner": player["nick"]}, {"$set": {"about": value}})
                    await message.reply(f"Описание города изменено на \"{value}\".")
                    
                elif arg == "pic":
                    await message.reply("Отправь фото города, подписав его \"/city_edit pic\".")
                    
                else:
                    await message.reply(f"Аргумента \"{arg}\" нет. Доступные:\n  - name - название\n  - players - горожане\n  - coords - координаты\n  - about - описание\n  - pic - фото (отправь как подпись к фото)")
        
        else:
            photo_file = message.photo[-1]
            file_id = photo_file.file_id

            await city_collection.update_one({"owner": player["nick"]}, {"$set": {"pic": file_id}})

            await message.reply("Фото города изменено.")

    else:
        await message.reply("У тебя нет города.")