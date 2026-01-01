import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message, LinkPreviewOptions, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatMemberStatus
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
bot_token = os.getenv('token')
cluster = AsyncIOMotorClient(os.getenv('db_link'))
chat_id = os.getenv('chat_id')
profile_collection = cluster.proj_one.profiles
ideas_collection = cluster.proj_one.ideas
achs_collection = cluster.proj_one.achievements

bot = Bot(token = bot_token, parse_mode = "html")
dp = Dispatcher()



async def profile(message: Message = None, id: int = None):
    if not id:
        if message.reply_to_message != None:
            player = message.reply_to_message.from_user
        else:
            player = message.from_user

        profile_data = await profile_collection.find_one({"_id": player.id})
    else:
        profile_data = await profile_collection.find_one({"_id": id})

    if profile_data != None:
        kb_profile = InlineKeyboardBuilder()

        kb_profile.button(text = "Общее", callback_data = f"p_1:{profile_data['_id']}")
        kb_profile.button(text = "Сервер", callback_data = f"p_2:{profile_data['_id']}")
        kb_profile.button(text = "Другое", callback_data = f"p_3:{profile_data['_id']}")
        if player == message.from_user:
            kb_profile.button(text = "⚙️ Настройки", callback_data = "profile_settings")
        kb_profile.button(text = "× Закрыть", callback_data = "close")

        kb_profile.adjust(3, 2)


        if not profile_data["hidden"]["name"]:
            name = profile_data['name']
        else:
            name = "<i>скрыто</i>"

        if not profile_data["hidden"]["age"]:
            age = f"{profile_data['age']} лет"
        else:
            age = "<i>скрыт</i>"

        bd_day = profile_data.get("bd", {}).get("day")
        bd_month = profile_data.get("bd", {}).get("month")

        if not profile_data["hidden"]["age"]:
            bd_year = "." + profile_data.get("bd", {}).get("year")
        else:
            bd_year = ""

        s = profile_data["s"]

        if not profile_data["hidden"]["country"]:
            country = profile_data["country"]
        else:
            country = "<i>скрыта</i>"

        bio = profile_data["bio"]
        pic = profile_data['pic']

        await message.reply(
            f'<b>Профиль игрока <a href="tg://user?id={player.id}">{player.full_name}</a></b> - общее\n\n'
            f'<b>Имя:</b> {name}\n'
            f'<b>Возраст:</b> {age}\n'
            f'<b>Пол:</b> {s}\n\n'
            f'<b>Страна:</b> {country}\n'
            f'<b>Дата рождения:</b> {bd_day}.{bd_month}{bd_year}\n\n'
            f'<b>О себе:</b> {bio}{pic}',
            reply_markup = kb_profile.as_markup(),
            link_preview_options = LinkPreviewOptions(prefer_small_media = True))
    else:
        if message.reply_to_message != None:
            await message.reply(f"У этого пользователя нет профиля!")
        else:
            await message.reply(f"У тебя ещё нет профиля! <b>Отправь команду /r,</b> чтобы начать регистрацию.")



async def p_1(call: CallbackQuery, need_to_create_keyboard: bool = False):
    id = int(call.data.split(':')[1])
    profile_data = await profile_collection.find_one({"_id": id})

    if need_to_create_keyboard:
        kb_profile = InlineKeyboardBuilder()

        kb_profile.button(text = "Общее", callback_data = f"p_1:{profile_data['_id']}")
        kb_profile.button(text = "Сервер", callback_data = f"p_2:{profile_data['_id']}")
        kb_profile.button(text = "Другое", callback_data = f"p_3:{profile_data['_id']}")
        kb_profile.button(text = "⚙️ Настройки", callback_data = "profile_settings")
        kb_profile.button(text = "× Закрыть", callback_data = "close")

        kb_profile.adjust(3, 2)

    if not profile_data["hidden"]["name"]:
        name = profile_data['name']
    else:
        name = "<i>скрыто</i>"

    if not profile_data["hidden"]["age"]:
        age = f"{profile_data['age']} лет"
    else:
        age = "<i>скрыт</i>"
    bd_day = profile_data.get("bd", {}).get("day")
    bd_month = profile_data.get("bd", {}).get("month")
    if not profile_data["hidden"]["age"]:
        bd_year = "." + profile_data.get("bd", {}).get("year")
    else:
        bd_year = ""
    s = profile_data["s"]
    if not profile_data["hidden"]["country"]:
        country = profile_data["country"]
    else:
        country = "<i>скрыта</i>"
    bio = profile_data["bio"]
    pic = profile_data['pic']

    if need_to_create_keyboard:
        markup = kb_profile.as_markup
    else:
        markup = call.message.reply_markup
    await call.message.edit_text(
        f'<b>Профиль игрока <a href="tg://user?id={profile_data["_id"]}">{profile_data["p_name"]}</a></b> - общее\n\n'
        f'<b>Имя:</b> {name}\n'
        f'<b>Возраст:</b> {age}\n'
        f'<b>Пол:</b> {s}\n\n'
        f'<b>Страна:</b> {country}\n'
        f'<b>Дата рождения:</b> {bd_day}.{bd_month}{bd_year}\n\n'
        f'<b>О себе:</b> {bio}{pic}',
        reply_markup = markup,
        link_preview_options = LinkPreviewOptions(prefer_small_media = True))
    

async def p_2(call: CallbackQuery):
    id = int(call.data.split(':')[1])
    profile_data = await profile_collection.find_one({"_id": id})


    s = profile_data["s"]
    try:
        pic = profile_data['pic']
    except KeyError:
        pic = ''
    nick = profile_data["nick"]
    join_day = profile_data.get("joined", {}).get("day")
    join_month = profile_data.get("joined", {}).get("month")
    join_year = profile_data.get("joined", {}).get("year")
    rep = profile_data["rep"]
    try:
        edition = profile_data["edition"]
    except KeyError:
        edition = '-'
    try:
        city = profile_data['city']
    except KeyError:
        city = ''

    try:
        achs = profile_data['achs']
    except KeyError:
        achs = []
    achs_list = '\n<b>Достижения:</b>\n'
    if achs != []:
        for ach in achs:
            ach_data = await achs_collection.find_one({'_id': ach})
            achs_list += f'    - 🥇 {ach_data["name"]}\n'
    else:
        achs_list = ''

    ideas = await ideas_collection.count_documents({'sender': profile_data['_id'], 'rate': 'approved'})
    if ideas > 0:
        i_count = f'<b>Одобренных идей:</b> {ideas}\n'
    else:
        i_count = ''

    if city != '':
        p_city = f'<b>Город:</b> {city}\n'
    else:
        p_city = ''

    if s == "мужской":
        await call.message.edit_text(
            f'<b>Профиль игрока <a href="tg://user?id={profile_data["_id"]}">{profile_data["p_name"]}</a></b> - сервер{pic}\n\n'
            f'<b>Xbox-ник:</b> {nick}\n'
            f'{p_city}\n'
            f'<b>Репутация:</b> {"{:,}".format(rep)}\n'
            f'{i_count}\n'
            f'<b>Играет на:</b> {edition}\n'
            f'<b>Присоединился:</b> {join_day}.{join_month}.{join_year}\n'
            f'{achs_list}',
            reply_markup = call.message.reply_markup,
            link_preview_options = LinkPreviewOptions(prefer_small_media = True))
    else:
        await call.message.edit_text(
            f'<b>Профиль игрока <a href="tg://user?id={profile_data["_id"]}">{profile_data["p_name"]}</a></b> - сервер{pic}\n\n'
            f'<b>Xbox-ник:</b> {nick}\n'
            f'{p_city}\n'
            f'<b>Репутация:</b> {"{:,}".format(rep)}\n'
            f'{i_count}\n'
            f'<b>Играет на:</b> {edition}\n'
            f'<b>Присоединилась:</b> {join_day}.{join_month}.{join_year}\n'
            f'{achs_list}',
            reply_markup = call.message.reply_markup,
            link_preview_options = LinkPreviewOptions(prefer_small_media = True))


async def p_3(call: CallbackQuery):
    id = int(call.data.split(':')[1])
    profile_data = await profile_collection.find_one({"_id": id})

    if (await call.message.chat.get_member(profile_data['_id'])).status == ChatMemberStatus.ADMINISTRATOR:
        inchat_status = 'админ'
    elif (await call.message.chat.get_member(profile_data['_id'])).status == ChatMemberStatus.CREATOR:
        inchat_status = 'владелец'
    elif (await call.message.chat.get_member(profile_data['_id'])).status == ChatMemberStatus.KICKED:
        inchat_status = 'забанен'
    elif (await call.message.chat.get_member(profile_data['_id'])).status == ChatMemberStatus.LEFT:
        inchat_status = 'вышел'
    elif (await call.message.chat.get_member(profile_data['_id'])).status == ChatMemberStatus.MEMBER or (await call.message.chat.get_member(profile_data['_id'])).status == ChatMemberStatus.RESTRICTED:
        inchat_status = 'участник'
    elif (await call.message.chat.get_member(profile_data['_id'])).can_send_messages == False:
        inchat_status = 'в муте'

    pic = profile_data['pic']
    await call.message.edit_text(
        f'<b>Профиль игрока <a href="tg://user?id={profile_data["_id"]}">{profile_data["p_name"]}</a></b> - другое{pic}\n\n'
        f'<b>Статус:</b> {inchat_status}\n'
        f'<b>ID:</b> <code>{profile_data["_id"]}</code>',
        reply_markup = call.message.reply_markup,
        link_preview_options = LinkPreviewOptions(prefer_small_media = True))