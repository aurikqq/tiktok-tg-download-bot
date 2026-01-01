import asyncio
import os
import datetime
import time
import random
import requests
import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command  # CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus
from functions.reg import *
from functions.edit_profile import *
from functions.idea_menu import *
from functions.rp import *
from functions.search_profile import *
from functions.time import *
from functions.game import *
from functions.profile import *
from functions.achievements import *
from functions.city_manager import *
from functions.profile_settings import *
from functions.states.states import RegisterState
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(filename = 'bot.log', level = logging.DEBUG)
logging.info(f'\n\n\nLogging Started at {datetime.datetime.now()}')

import keyboards

load_dotenv()
bot_token = os.getenv('token')
chat_id = os.getenv('chat_id')
rp_commands = ['!обнять', '!укусить', '!сжечь', '!убить', '!трахнуть', '!пригласитьчай', '!чай', '!кофе',
               '!пригласитькофе', '!ударить', '!поцеловать', '!похоронить', '!ядерка', '!послать', '!погладить',
               '!покормить', '!съесть', '!бухать']

bot = Bot(token = bot_token, default = DefaultBotProperties(parse_mode = 'html'))
dp = Dispatcher()

cluster = AsyncIOMotorClient(os.getenv('db_link'))
profile_collection = cluster.proj_one.profiles
ideas_collection = cluster.proj_one.ideas
data_collection = cluster.proj_one.data

offset = 0

dp.message.register(start_reg, Command("r"))
dp.message.register(save_name, RegisterState.reg_name_state)
dp.message.register(save_nick, RegisterState.reg_nick_state)
dp.message.register(save_bd, RegisterState.reg_bd_state)
dp.message.register(save_s, RegisterState.reg_s_state)
dp.message.register(save_country, RegisterState.reg_country_state)

dp.message.register(edit_start, Command("edit"))
dp.message.register(edit_profile, RegisterState.edit_profile_state)
dp.message.register(edit_bd, RegisterState.edit_bd_state)
dp.message.register(edit_join, RegisterState.edit_join_state)
dp.message.register(edit_end, RegisterState.end_profile_state)
dp.message.register(confirm_delete, RegisterState.delete_profile_state)

dp.message.register(set_id, RegisterState.ach_id_state)
dp.message.register(set_name, RegisterState.ach_name_state)
dp.message.register(save_ach, RegisterState.ach_desc_state)
dp.message.register(start_adding, Command('ach_add'))
dp.message.register(give_ach, Command('ach'))
dp.message.register(take_ach, Command('ach_take'))
dp.message.register(del_ach, Command('ach_del'))
dp.message.register(ach_help, Command('ach_help'))
dp.message.register(achs_list, Command('ach_list'))
dp.callback_query.register(ach_back, lambda query: query.data == 'to_list')

dp.message.register(act, F.text.split(' ', 1)[0].in_(rp_commands))
dp.message.register(me, Command('me'))

dp.message.register(idea_suggest, Command('suggest', 's'))
dp.message.register(idea_renaming, Command('rename'))
dp.message.register(approved_list, Command('ideas'))

dp.callback_query.register(idea_menu, lambda query: query.data == 'menu')
dp.callback_query.register(idea_rate, lambda query: query.data == 'idea_rate')
dp.callback_query.register(idea_rename, lambda query: query.data == 'idea_rename')
dp.callback_query.register(idea_approve, lambda query: query.data == 'idea_rate_approve')
dp.callback_query.register(idea_dismiss, lambda query: query.data == 'idea_rate_dismiss')
dp.callback_query.register(idea_punish, lambda query: query.data == 'idea_rate_punish')
dp.callback_query.register(idea_cancel, lambda query: query.data == 'idea_cancel')
dp.callback_query.register(idea_rate_cancel, lambda query: query.data == 'idea_rate_cancel')
dp.callback_query.register(idea_rate_send, lambda query: query.data == 'idea_rate_send')

dp.message.register(search_profile, Command('find'))

dp.message.register(play, Command('rice'))
dp.message.register(pl_stats, Command('rice_p'))
dp.message.register(stats, Command('rice_stats'))

dp.message.register(city_preadd, Command('city_add'))
dp.message.register(about_city, Command('city'))
dp.message.register(delete_city, Command('city_delete'))
dp.message.register(edit_city, Command('city_edit'))
dp.message.register(cities_list, Command('city_list'))
dp.callback_query.register(city_add, lambda query: query.data == 'city_continue')
dp.callback_query.register(save_city, lambda query: query.data == 'right')
dp.callback_query.register(edit_city, lambda query: query.data == 'change')
dp.callback_query.register(edit_city, lambda query: query.data == 'city_edit_back')
dp.callback_query.register(city_edit_name, lambda query: query.data == 'city_name')
dp.callback_query.register(city_edit_citizens, lambda query: query.data == 'city_citizens')
dp.callback_query.register(city_edit_coords, lambda query: query.data == 'city_coords')
dp.callback_query.register(city_add_cancel, lambda query: query.data == 'city_cancel')
dp.callback_query.register(city_back, lambda query: query.data == 'city_back')
dp.message.register(city_count, RegisterState.city_name_state)
dp.message.register(city_citizens, RegisterState.city_citizens_state)
dp.message.register(city_coords, RegisterState.city_coords_state)
dp.message.register(city_edited_name, RegisterState.city_name_edit_state)
dp.message.register(city_edited_citizens, RegisterState.city_citizens_edit_state)
dp.message.register(city_edited_coords, RegisterState.city_coords_edit_state)
dp.message.register(city_edited_coords, RegisterState.city_coords_edit_state)


dp.message.register(time_menu, Command('time'))
dp.message.register(profile, F.text.lower().in_({'!п', '!профиль'}))
dp.callback_query.register(profile_settings, lambda query: query.data == "profile_settings" or query.data == "back_to_ps")
dp.callback_query.register(hide_data, lambda query: query.data == "hide_data")
dp.callback_query.register(add_data, lambda query: query.data == "add_data" or query.data == "back_to_add_data")
dp.callback_query.register(delete_profile, lambda query: query.data == "delete_profile")
dp.callback_query.register(hide_name, lambda query: query.data == "hide_name")
dp.callback_query.register(hide_age, lambda query: query.data == "hide_age")
dp.callback_query.register(hide_country, lambda query: query.data == "hide_country")
dp.callback_query.register(add_bio, lambda query: query.data == "add_bio")
dp.callback_query.register(add_pic, lambda query: query.data == "add_pic")
dp.callback_query.register(add_edition, lambda query: query.data == "add_edition")
dp.callback_query.register(remove_bio, lambda query: query.data == "remove_bio")
dp.callback_query.register(remove_pic, lambda query: query.data == "remove_pic")
dp.callback_query.register(remove_edition, lambda query: query.data == "remove_edition")
dp.callback_query.register(delete_yes, lambda query: query.data == "delete_yes")
dp.callback_query.register(back_to_profile, lambda query: query.data.startswith("ps_back"))

dp.callback_query.register(country_1, lambda query: query.data == 'back')
dp.callback_query.register(country_2, lambda query: query.data == 'next')
dp.callback_query.register(close, lambda query: query.data == 'close')
dp.callback_query.register(country, lambda query: query.data == 'BY' or query.data == 'UA' or query.data == 'KZ' or query.data == 'AZ' or query.data == 'SE' or query.data == 'UZ' or query.data == 'DE' or query.data == 'RU')


@dp.message(Command('test'))  # для фикса бд и прочих мелочей
async def test(message: Message):
    await profile_collection.update_many({}, {'$set': {"hidden": {"name": False, "age": False, "country": False}}})
    await message.answer("done")

@dp.message(Command('msg_count'))
async def msg(message: Message):
    await message.reply(f'Всего сообщений в чате: <b>{message.message_id + 1}</b>')

@dp.message(Command('edition'))
async def set_edition(message: Message):
    profile_data = await profile_collection.find_one({"_id": message.from_user.id})
    if profile_data is None:
        await message.reply(f'У тебя ещё нет профиля!<b>Отправь команду</b> /r, чтобы создать его.')
    else:
        await message.reply(f'<b>Выбери издание Майнкрафта</b>, с которого ты играешь на сервере.',
                            reply_markup=keyboards.kb_edition)


@dp.callback_query(lambda query: query.data == 'java')
async def set_java(call: CallbackQuery):
    await call.message.reply('Выбрано <b>Java Edition.</b>')
    await profile_collection.update_one({'_id': call.from_user.id},
                                        {'$set': {'edition': 'Java Edition'}})
    await call.answer()


@dp.callback_query(lambda query: query.data == 'bugrock')
async def set_bugrock(call: CallbackQuery):
    await call.message.reply('Выбрано <b>Bedrock Edition.</b>')
    await profile_collection.update_one({'_id': call.from_user.id},
                                        {'$set': {'edition': 'Bedrock Edition'}})
    await call.answer()


@dp.callback_query(lambda query: query.data == 'both')
async def set_both(call: CallbackQuery):
    await call.message.reply('Выбраны <b>оба издания.</b>')
    await profile_collection.update_one({'_id': call.from_user.id},
                                        {'$set': {'edition': 'Java и Bedrock'}})
    await call.answer()


@dp.callback_query(lambda query: query.data[:3] == 'p_1')
async def switch_profile(call: CallbackQuery):
    if (await call.message.chat.get_member(call.from_user.id)).status in [ChatMemberStatus.ADMINISTRATOR,
                                                                          ChatMemberStatus.CREATOR] or call.from_user.id == call.message.reply_to_message.from_user.id:
        await p_1(call)
    else:
        await call.answer('Взаимодействовать с профилем может только открывший его игрок и админы.')


@dp.callback_query(lambda query: query.data[:3] == 'p_2')
async def switch_profile(call: CallbackQuery):
    if (await call.message.chat.get_member(call.from_user.id)).status in [ChatMemberStatus.ADMINISTRATOR,
                                                                          ChatMemberStatus.CREATOR] or call.from_user.id == call.message.reply_to_message.from_user.id:
        await p_2(call)
    else:
        await call.answer('Взаимодействовать с профилем может только открывший его игрок и админы.')


@dp.callback_query(lambda query: query.data[:3] == 'p_3')
async def switch_profile(call: CallbackQuery):
    if (await call.message.chat.get_member(call.from_user.id)).status in [ChatMemberStatus.ADMINISTRATOR,
                                                                          ChatMemberStatus.CREATOR] or call.from_user.id == call.message.reply_to_message.from_user.id:
        await p_3(call)
    else:
        await call.answer('Взаимодействовать с профилем может только открывший его игрок и админы.')


@dp.callback_query(lambda query: query.data == 'delete')
async def delete_profile(call: CallbackQuery):
    if (await call.message.chat.get_member(call.from_user.id)).status in [ChatMemberStatus.ADMINISTRATOR,
                                                                          ChatMemberStatus.CREATOR] or call.from_user.id == call.message.reply_to_message.from_user.id:
        await call.message.edit_text(f'<b>{call.from_user.full_name}</b> удалил сообщение.')
        time.sleep(3)
        await bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        await call.answer('Профиль может закрыть только открывший его игрок и админы.')

'''
@dp.message(Command('set_ip'))
async def set_ip(message: Message):
    if len(message.text) > len('/set_ip'):
        ip = '/' + message.text.split(' ', 1)[1]
        profile_data = await profile_collection.find_one({"_id": message.from_user.id})
        if profile_data is None:
            await message.reply(f'У тебя ещё нет профиля!<b>Отправь команду</b> /r, чтобы создать его.')
        else:
            path = 'C:\\Users\\Administrator\\Desktop\\bolt3\\player_ips\\' + profile_data['nick'] + '.txt'
            if not os.path.exists(path):
                with open(path, 'w') as file:
                    file.write(ip)
                await message.reply(f'IP-адрес для игрока <b>{profile_data["nick"]}</b> добавлен!')
            else:
                with open(path, 'a') as file:
                    file.write(f' {ip}')
                await message.reply(f'IP-адрес для игрока <b>{profile_data["nick"]}</b> добавлен!')
            await message.delete()
    else:
        if (await bot.get_chat(message.chat.id)).type == 'private':
            await message.reply(
                f'Для защиты сервера на него можно зайти <b>только с разрешённых IP-адресов</b>. При первом входе твой IP сохраняется, но ты можешь добавить другие.\n\nЕсли твоего текущего адреса нет в разрешенных, <b>нажми кнопку на Reply-клавиатуре или введи /set_ip <code>[ip]</code>.</b>',
                reply_markup=keyboards.kb_ip)
        elif (await bot.get_chat(message.chat.id)).type == 'group' or (
                await bot.get_chat(message.chat.id)).type == 'supergroup':
            await message.reply(
                f'Для защиты сервера на него можно зайти <b>только с разрешённых IP-адресов</b>. При первом входе твой IP сохраняется, но ты можешь добавить другие.\n\nЕсли твоего текущего адреса нет в разрешенных, <b>добавь его</b> командой /set_ip <code>[ip]</code> или просто <b>напиши</b> /set_ip в ЛС боту, если не знаешь свой адрес.')
'''

@dp.message(F.web_app_data)
async def get_ip(web_app_message):
    ip = '/' + web_app_message.web_app_data.data
    profile_data = await profile_collection.find_one({"_id": web_app_message.from_user.id})
    if profile_data is None:
        await web_app_message.reply(f'У тебя ещё нет профиля!<b>Отправь команду</b> /r, чтобы создать его.')
    else:
        path = 'D:\\java_server\\player_ips\\' + profile_data['nick'] + '.txt'
        if not os.path.exists(path):
            with open(path, 'w') as file:
                file.write(ip)
                await web_app_message.reply(f'IP-адрес для игрока <b>{profile_data["nick"]}</b> добавлен!')
        else:
            with open(path, 'a') as file:
                file.write(f' {ip}')
                await web_app_message.reply(f'IP-адрес для игрока <b>{profile_data["nick"]}</b> добавлен!')


@dp.message(Command('bio'))
async def bio(message: Message):
    if len(message.text) > len('/bio'):
        if len(message.text) <= 150:
            bio = message.text.split(' ', 1)[1]
            await profile_collection.update_one({"_id": message.from_user.id}, {"$set": {"bio": bio}})
            await message.reply(f'<b>Описание профиля</b> установлено!')
        else:
            await message.reply(f'<b>Введи описание</b> короче 150-и символов.')
    else:
        await message.reply(f'<b>Введи описание</b> после команды, чтобы установить его.')


@dp.message(Command('pic'))
async def bio_pic(message: Message):
    if len(message.text) > len('/pic'):
        url = message.text.split(' ', 1)[1]
        if url != 'delete':
            response = requests.head(url)
            if response.status_code == 200 and 'image' in response.headers.get('content-type'):
                await profile_collection.update_one({"_id": message.from_user.id},
                                                    {"$set": {"pic": f'<a href="{url}"> </a>'}})
                await message.reply(f'<b>Фото профиля</b> установлено!')
            else:
                await message.reply(
                    f'<b>Эта ссылка не ведет</b> напрямую на фото!\n\nВот пример правильной ссылки: https://w.wallhaven.cc/full/p8/wallhaven-p8z9pj.png',
                    disable_web_page_preview=True)
        else:
            if (await message.chat.get_member(message.from_user.id)).status in [ChatMemberStatus.ADMINISTRATOR,
                                                                                ChatMemberStatus.CREATOR]:
                if message.reply_to_message is not None:
                    await message.reply(
                        f'Фото профиля игрока <a href="tg://user?id={message.reply_to_message.from_user.id}"><b>{message.reply_to_message.from_user.full_name}</b></a> удалено.')
                    await profile_collection.update_one({"_id": message.reply_to_message.from_user.id},
                                                        {"$set": {"pic": ''}})
                else:
                    await profile_collection.update_one({"_id": message.from_user.id}, {"$set": {"pic": ''}})
                    await message.reply(f'Фото профиля удалено.')

    else:
        await message.reply(
            f'<b>Введи прямую ссылку</b> после команды, чтобы добавить фото, или <code>/pic delete</code>, чтобы его удалить.\n\nПример: <code>/pic https://w.wallhaven.cc/full/p8/wallhaven-p8z9pj.png</code>',
            disable_web_page_preview=True)


@dp.message(Command('id'))
async def id(message: Message):
    if message.reply_to_message is None:
        await message.reply(f'Чат: <code>{message.chat.id}</code>\nИгрок: <code>{message.from_user.id}</code>')
    else:
        await message.reply(
            f'Чат: <code>{message.chat.id}</code>\nИгрок: <code>{message.from_user.id}</code>\nИгрок в ответе: <code>{message.reply_to_message.from_user.id}</code>')


@dp.message(Command('ip'))
async def ip(message: Message):
    ip = await data_collection.find_one({"_id": 'ip'})
    java_port = await data_collection.find_one({"_id": 'java_port'})
    bedrock_port = await data_collection.find_one({"_id": 'bedrock_port'})
    await message.reply(
        f'<b>Основной сервер</b>\n\n'
        f'<b>IP:</b> <code>{ip["value"]}</code>\n'
        f'<b>Порт</b>\n'
        f'    - Java: {java_port["value"]}\n'
        f'    - Bedrock: {bedrock_port["value"]}')
    
@dp.message(F.text.lower() == '!айпи' or '!ip' or '/айпи')
async def ip(message: Message):
    ip = await data_collection.find_one({"_id": 'ip'})
    java_port = await data_collection.find_one({"_id": 'java_port'})
    bedrock_port = await data_collection.find_one({"_id": 'bedrock_port'})
    await message.reply(
        f'<b>Основной сервер</b>\n\n'
        f'<b>IP:</b> <code>{ip["value"]}</code>\n'
        f'<b>Порт</b>\n'
        f'    - Java: {java_port["value"]}\n'
        f'    - Bedrock: {bedrock_port["value"]}')

@dp.message(Command('set_data'))
async def set_data(message: Message):
    data_id = message.text.split(' ', 1)[1].split(' ', 1)[0]
    data = await data_collection.find_one({'_id': data_id})
    value = (message.text.split(' ', 1)[1]).split(' ', 1)[1]
    if data:
        query = {"_id": data_id}
        update = {"$set": {"value": value}}
        await data_collection.update_one(query, update)

        await message.reply(f'Значение <b>{value}</b> установлено для переменной <b>{data_id}</b>.')
    else:
        data_pattern = {
        '_id': data_id, 
        'value': value,
        }
        data_collection.insert_one(data_pattern)
        await message.reply(f'Создана переменная <b>{data_id}</b> со значением <b>{value}</b>.')


@dp.message(Command('bot'))
async def work(message: Message):
    if message.from_user.id == 1104899353:
        await message.reply('Создатель... та иди ты, хватит меня ломать')
    elif message.from_user.id == 824723708:  #Никто
        await message.reply('Без малого района Мартин Лютер Кинг?')
    elif message.from_user.id == 6655286856:  #Кирпич
        await message.reply("God dammit, where the fuck we're?!")
    elif message.from_user.id == 1075813778:  #Джейн
        await message.reply('Шедевроглавчертилабанкирпрезидентпандатрап... эм..ладно, забыл, здарова короче')
    elif message.from_user.id == 1456378239:  #Элита
        await message.reply('Хейтер травы, небось и не трогал её ни разу...')
    elif message.from_user.id == 1084352018:  #Фриск
        await message.reply('Есть два стула - на одном 16-ый бан, на другом рейд Фрискограда...')
    elif message.from_user.id == 1621354695:  #игнор
        await message.reply('Украинский патриот-зетник??? Интересно...')
    elif message.from_user.id == 1142012357:  #Кеклеша
        await message.reply('На месте (спасибо тебе за всё!)')
    elif message.from_user.id == 1022037422:  #Неро
        await message.reply('Понабирают всяких ботоломателей...')
    elif message.from_user.id == 531183183:  #Айс
        await message.reply('Когда свадьба с Люциком?')
    elif message.from_user.id == 1133419266:  #Люцик
        await message.reply('Шедевронацист на админе?')
    elif message.from_user.id == 6200650451:  #Кирилл
        await message.reply('Чем-то мы похожи...')
    elif message.from_user.id == 1445435997:  #Рю
        await message.reply('Псих, шизик, обуза... это я про себя, вылазь из скалка и пошли в майн, бро')
    elif message.from_user.id == 5524543639:  #Денди
        await message.reply('НЕ ТРОГАЙ ХОСТ БЛЯТБ...')
    elif message.from_user.id == 1080296062:  #Вентиль
        await message.reply('Миллиардер, плейбой, мэр Новосиба, мужик мечты... кстати, когда видос?')
    elif message.from_user.id == 5113349442:  #Хуг
        await message.reply('Халф-лайф 3 выйдет завтра, если не вышел - перечитай это')
    else:
        await message.reply('На месте!')


@dp.message(Command("help_rp"))
async def help(message: Message):
    await message.reply(
        f'<b>Список РП-команд бота:</b>\n\n'
        f'- /me <code>[текст]</code> - сделать что-то.\n  Пример: /me написал команду\n\n'
        f'!обнять\n!поцеловать\n!укусить\n!ударить\n!сжечь\n!убить\n!похоронить\n!послать\n!погладить\n!покормить\n!чай\n!кофе\n!пригласитьчай\n!пригласитькофе\n!съесть\n!бухать\n!ядерка\n\n'
        f'<b>Все РП-команды работают, если ответить ими на другого пользователя или написать что-то после команды.</b>\nПример: <code>!чай @projectsone_bot</code>.'
    )


@dp.message(Command("help"))
async def help(message: Message):
    await message.reply(
        f'<b>Помощь по чату</b>\n'
        f'- <b><a href="https://telegra.ph/Pravila-chata-Project-One-07-05">Правила чата</a></b>\n\n'
        f'<b>Топики</b>\n'
        f'    - <a href="https://t.me/+uTUiKmLHx9ljNTIy">Чат с топиками и чатлогом</a>\n'
        f'    - <a href="https://telegra.ph/Spisok-topikov-chata-Project-One-03-02">Правила топиков</a>',
        disable_web_page_preview = True,
        reply_markup=keyboards.kb_help)

@dp.callback_query(lambda query: query.data == 'help_chat')
async def chat_help(call: CallbackQuery):
    await call.message.edit_text(
        f'<b>Помощь по чату</b>\n'
        f'- <b><a href="https://telegra.ph/Pravila-chata-Project-One-07-05">Правила чата</a></b>\n\n'
        f'<b>Топики</b>\n'
        f'    - <a href="https://t.me/+uTUiKmLHx9ljNTIy">Чат с топиками и чатлогом</a>\n'
        f'    - <a href="https://telegra.ph/Spisok-topikov-chata-Project-One-03-02">Правила топиков</a>',
        disable_web_page_preview = True,
        reply_markup=keyboards.kb_help)

@dp.callback_query(lambda query: query.data == 'help_server')
async def server_help(call: CallbackQuery):
    await call.message.edit_text(
        f'<b>Помощь по серверу</b>\n'
        f'- <b><a href="https://telegra.ph/Pravila-servera-Project-One-07-06">Правила сервера</a></b>\n\n'
        f'<b>Новые игроки</b>\n'
        f'    - Пособие для новичков\n'
        f'    - Как пригласить друга?\n\n'
        f'<b>Города</b>\n'
        f'    - <a href="https://telegra.ph/Pravila-osnovaniya-gorodov-06-16">Основание города</a>',
        disable_web_page_preview = True,
        reply_markup=keyboards.kb_help)

@dp.callback_query(lambda query: query.data == 'help_bot')
async def bot_help(call: CallbackQuery):
    await call.message.edit_text(
        f'<b>Помощь по боту</b>\n'
        f'    - <a href="https://telegra.ph/Komandy-bota-Project-One-01-28">Команды бота</a>\n'
        f'    - <a href="https://telegra.ph/Kratkij-gajd-po-botu-Project-One-01-28">Гайд по боту</a>\n\n'
        f'<b>Профили</b>\n'
        f'    - Параметры профиля\n'
        f'    - <a href="https://telegra.ph/Kak-ustanovit-foto-profilya-v-bote-03-09">Как установить фото профиля</a>'
        f'<i>Версия бота: 0.9.1</i>',
        disable_web_page_preview = True,
        reply_markup=keyboards.kb_help)

@dp.callback_query(lambda query: query.data == 'help_credits')
async def show_credits(call: CallbackQuery):
    await call.answer('Основной разработчик - Айрик\nПомощь с обучением - Айс\nIP-логгер в /set_ip (не используется): Ляпис', show_alert = True)


@dp.message(Command("dang"))
async def dang(message: Message):
    await message.reply(
        f'<a href="https://telegra.ph/Post-dlya-teh-kto-ne-sharit-chto-takoe-Dangerous-i-kto-takoj-YUra-03-09-4">Пост для тех, кто не знает о Данжероусе и его создателе.</a>')


@dp.message(F.text.lower() == '!юра')
async def fucker(message: Message):
    acts = ['трахнул(а) юру', 'поимел(а) юру', 'затрахал(а) юру до смерти', 'взорвал(а) юру', 'расстреляла(а) юру',
            'заманила(а) юру в газовую камеру', 'перевез(ла) юру в Россию', 'сжег(ла) юру',
            'сбросил(а) на юру пару тонн демократии', 'порвал(а) жопу юре', 'снес(ла) юре хост', 'кончил(а) на юру',
            'сдал юру полиции']
    await message.reply(
        f'<b><a href = "tg://user?id={message.from_user.id}">{message.from_user.full_name}</a></b> {random.choice(acts)}!')


@dp.message(Command('admins'))
async def fuck_adm(message: Message):
    msg = await message.reply('Выбираю случайного админа...')
    time.sleep(3)
    await msg.edit_text(f'Выбран админ <b><a href="tg://user?id=1133419266">Люцик</a></b>.\nИщу его IP...')
    time.sleep(3)
    await msg.edit_text(
        f'Выбран админ <b><a href="tg://user?id=1133419266">Люцик</a></b>.\nIP найден.\nВычисляю адрес...')
    time.sleep(5)
    await msg.edit_text(
        f'Выбран админ <b><a href="tg://user?id=1133419266">Люцик</a></b>.\nIP найден.\nАдрес вычислен.\nВыполняю операцию...')
    time.sleep(7)
    await msg.edit_text(
        f'Выбран админ <b><a href="tg://user?id=1133419266">Люцик</a></b>.\nIP найден.\nАдрес вычислен.\n<b>Операция выполнена.</b>\n\n<b>Дом админа заминирован.</b>')
    time.sleep(1)
    await msg.edit_text(
        f'Выбран админ <b><a href="tg://user?id=1133419266">Люцик</a></b>.\nIP найден.\nАдрес вычислен.\n<b>Операция выполнена.</b>\n\n<b>Дом админа заминирован.</b> У него есть <b>10 сек.</b>, чтобы собрать манатки и мыльнуть из дома.')
    timer = 11
    while timer > 0:
        timer -= 1
        await msg.edit_text(
            f'Выбран админ <b><a href="tg://user?id=1133419266">Люцик</a></b>.\nIP найден.\nАдрес вычислен.\n<b>Операция выполнена.</b>\n\n<b>Дом админа заминирован.</b> У него есть <b>{timer} сек.</b>, чтобы собрать манатки и мыльнуть из дома.')
        time.sleep(1)
    await msg.edit_text(
        f'Выбран админ <b><a href="tg://user?id=1133419266">Люцик</a></b>.\nIP найден.\nАдрес вычислен.\n<b>Операция выполнена.</b>\n\n<b>Дом админа заминирован.</b> Время вышло, админ остался без дома и теперь едет работать снарядом под Бахмут в надежде прокормиться.')


@dp.message(F.text[0] == '+')
async def plus_rep(message: Message):
    if message.reply_to_message is not None and message.reply_to_message.from_user != message.from_user:
        user = await profile_collection.find_one({"_id": message.reply_to_message.from_user.id})
        query = {"_id": user["_id"]}
        update = {"$inc": {"rep": 1}}
        await profile_collection.update_one(query, update)
        await message.reply(
            f'Репутация игрока <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b> повышена на 1 <i>(теперь {user["rep"] + 1})</i>.',
            reply_markup=keyboards.kb_cancel)


@dp.callback_query(lambda query: query.data == 'cancel')
async def cancel_rep(call: CallbackQuery):
    if call.from_user == call.message.reply_to_message.from_user:
        user = await profile_collection.find_one({"_id": call.message.reply_to_message.from_user.id})
        query = {"_id": user["_id"]}
        update = {"$inc": {"rep": -1}}
        await profile_collection.update_one(query, update)
        await call.message.edit_text(f'Повышение репутации <b>отменено</b>.')
        time.sleep(3)
        await bot.delete_message(call.message.chat.id, call.message.message_id)


@dp.message(Command('rep'))
async def rep_edit(message: Message):
    if (await message.chat.get_member(message.from_user.id)).status not in [ChatMemberStatus.ADMINISTRATOR,
                                                                            ChatMemberStatus.CREATOR]:
        await message.reply('Ты не админ!')
    else:
        if len(message.text) > len('/rep'):
            if message.reply_to_message is not None:
                rep_count = int(message.text.split(' ', 1)[1].split(' ', 1)[0])
                if message.text.count(' ') > 1:
                    rep_reason = message.text.split(' ', 1)[1].split(' ', 1)[1]
                user = await profile_collection.find_one({"_id": message.reply_to_message.from_user.id})
                query = {"_id": user["_id"]}
                if rep_reason != None:
                    if rep_count > 0:
                        update = {"$inc": {"rep": rep_count}}
                        await message.reply(
                            f'Репутация игрока <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b> повышена на {"{:,}".format(rep_count)}.\n<b>Причина:</b> {rep_reason}.')
                    if rep_count < 0:
                        update = {"$inc": {"rep": rep_count}}
                        await message.reply(
                            f'Репутация игрока <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b> понижена на {"{:,}".format(abs(rep_count))}.\n<b>Причина:</b> {rep_reason}.')
                    if rep_count == 0:
                        update = {"$set": {"rep": 0}}
                        await message.reply(
                            f'Репутация игрока <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b> обнулена.\n<b>Причина:</b> {rep_reason}.')
                else:
                    if rep_count > 0:
                        update = {"$inc": {"rep": rep_count}}
                        await message.reply(
                            f'Репутация игрока <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b> повышена на {"{:,}".format(rep_count)}.')
                    if rep_count < 0:
                        update = {"$inc": {"rep": rep_count}}
                        await message.reply(
                            f'Репутация игрока <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b> понижена на {"{:,}".format(abs(rep_count))}.')
                    if rep_count == 0:
                        update = {"$set": {"rep": 0}}
                        await message.reply(
                            f'Репутация игрока <b><a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.full_name}</a></b> обнулена.')

                await profile_collection.update_one(query, update)
            else:
                await message.reply(f'<b>Ответь на сообщение</b> игрока, чтобы поменять его репутацию.')
        else:
            await message.reply(f'<b>Введи количество</b> репутации, которое нужно добавить или отнять.')


@dp.message(Command('msg'))
async def dm(message: Message):
    if len(message.text) == len('/msg') or message.text.count(' ') < 2:
        await message.reply(
            '<b>Введи ID пользователя и текст</b> сообщения, которое хочешь ему отправить.\n\n<b>Пример:</b> <code>/msg 1010010110 сообщение</code>; сообщение должно идти после ID.')
    try:
        id = int(message.text.split('/msg ', 1)[1].split(' ', 1)[0])
        text = message.text.split(f'{str(id)} ', 1)[1]
        await bot.send_message(id, f'<b>Тебе отправили анонимное сообщение:</b>\n\n<blockquote>{text}</blockquote>')
        await message.reply(
            f'Анонимное сообщение отправлено пользователю <b><a href="tg://user?id={id}">{(await bot.get_chat(id)).full_name}</a></b>.')
        await bot.send_message(1104899353,
                               f'Сообщение от <a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a> для <a href="tg://user?id={id}">{(await bot.get_chat(id)).full_name}</a>:\n\n{text}')
    except TelegramBadRequest:
        await message.reply(
            f'У игрока нет лички с ботом, поэтому отправить ему сообщение <b>невозможно</b>, пока он не напишет боту <b>/start</b>.')

@dp.message(Command('force_bday'))
async def birthday_search(msg: Message):
    if datetime.date.today().day < 10:
        day = "0" + str(datetime.date.today().day)
    else:
        day = str(datetime.date.today().day)
    if datetime.date.today().month < 10:
        month = "0" + str(datetime.date.today().month)
    else:
        month = str(datetime.date.today().month)
    users = await profile_collection.find({"bd.day": day, "bd.month": month}).to_list(100)
    for user in users:
        chat = await bot.get_chat(user["_id"])
        msg = await bot.send_message(chat_id,
                                     f'Сегодня день рождения у игрока <b><a href="tg://user?id={user["_id"]}">{chat.first_name}</a></b>, которому исполнилось {user["age"] + 1} лет.\n\n<b>Поздравляем!</b> 🎉')
        await bot.pin_chat_message(chat_id, msg.message_id)
        query = {"_id": user["_id"]}
        update = {"$inc": {"age": 1}}
        await profile_collection.update_one(query, update)

        if (await bot.get_chat_member(chat_id, user["_id"])).status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            await bot.promote_chat_member(chat_id, user["_id"], can_pin_messages = True)
            was_admin = False
        else:
            was_admin = True
        await bot.set_chat_administrator_custom_title(chat_id, user["_id"], 'Именинник')
        time.sleep(86400)
        if not was_admin:
            await bot.promote_chat_member(chat_id, user["_id"], can_pin_messages=False)
        """
        if chat.username != None:
            text = f'{chat.username}, с днем рождения!'
        kb_edit = ReplyKeyboardMarkup(
	        keyboard = [
		    [
			    KeyboardButton(text = "Имя"),
		    ]
	    ],
        resize_keyboard = True,
        one_time_keyboard = True,
        selective = True,
        )
        """


async def bd_check():
    while True:
        current_time = datetime.datetime.now().time()
        if current_time.hour == 0 and current_time.minute == 0:
            await birthday_search(None)
        await asyncio.sleep(60)


async def check_nicks(profile):
    profiles = profile_collection.find({})
    async for profile in profiles:
        user = await bot.get_chat_member(chat_id, profile['_id'])
        await profile_collection.update_one({'_id': user.user.id}, {'$set': {'p_name': user.user.full_name}})
        await profile_collection.update_one({'_id': user.user.id}, {'$set': {'username': user.user.username}})
    await asyncio.sleep(600)


@dp.message(Command('nerf_cg'))
async def catgirls_nerf(message: Message, profile):
    profiles = profile_collection.find({})
    async for profile in profiles:
        update = {'game.catgirls': {'$gte': 1, '$lte': 5}, '_id': profile['_id']}
        query = {'$inc': {'game.rice': (profile.get("game", {})).get("catgirls")} * -1}
        await profile_collection.update_one(update, query)
    await message.reply('Готово.')


async def catgirls_work(profile):
    profiles = profile_collection.find({})
    async for profile in profiles:
        update = {'game.catgirls': {'$gte': 1, '$lte': 5}, '_id': profile['_id']}
        query = {'$inc': {'game.rice': (profile.get("game", {})).get("catgirls")}}
        await profile_collection.update_one(update, query)
    await asyncio.sleep(86400)


async def on_startup():
    print('Bot is On.')
    send_start_message = input('Do you wanna send a Start Message (Yes / No)? ')
    if send_start_message.lower() == 'yes':
        await bot.send_message(chat_id, 'Бот запущен.')
        print('Start Message was sent to the Chat.')
    else:
        print("Start Message wasn't sent to the Chat.")

async def start_tasks():
    await asyncio.create_task(bd_check())
    await asyncio.create_task(check_nicks())
    await asyncio.create_task(catgirls_work())

dp.startup.register(on_startup)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, on_startup=on_startup)
    await start_tasks()


@dp.message(Command('off'))
async def off(message: Message):
    if (await message.chat.get_member(message.from_user.id)).status not in [ChatMemberStatus.ADMINISTRATOR,
                                                                            ChatMemberStatus.CREATOR]:
        await message.reply('Ты не админ!')
    else:
        await message.reply('Бот отключен.')
        await dp.stop_polling()

if __name__ == "__main__":
    asyncio.run(main())
