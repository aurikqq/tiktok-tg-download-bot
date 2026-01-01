import csv
import os
import re
import time

from aiogram.exceptions import TelegramForbiddenError
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv('token')
chat_id = os.getenv('chat_id')
logs_dir = os.getenv('pl_logs_dir')

bot = Bot(token=bot_token, parse_mode="html")
dp = Dispatcher()


async def search_logs(message: Message):
    await message.reply('Команда временно недоступна')
'''
    if message.text == '/logs':
        await message.reply(
            f'<b>Введи координаты и дату</b> после команды в формате <code>/logs -256 64 0 31.01</code>')
    else:
        if message.text.count(' ') == 4:
            args = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', message.text)
            coords = [int(args[0]), int(args[1]), int(args[2])]
            date = args[-1]

            with open(logs_dir + f'BehaviorLog-2024-{date[3:]}-{date[:2]}.csv', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                result = f'Логи по координатам <b>{coords[0]} {coords[1]} {coords[2]}</b> за дату <b>{date[:2]}.{date[3:]}:</b>\n\n'
                found = ''
                found_count = 0

                for row in reader:
                    if str(row[8]) == str(coords[0]) and str(row[9]) == str(coords[1]) and str(row[10]) == str(
                            coords[2]):
                        source = row[2]
                        dim = row[1]
                        e_time = row[0]
                        event = row[6]
                        info = row[11]
                        if event == 'Take out from Container':
                            found += f'<b>{source}</b> в <b>{e_time.split(" ", 1)[1][:5]}</b> взял из контейнера вещь (слот {info.split("Slot ", 1)[1]}) в измерении <b>{dim}</b>.\n\n'
                        elif event == 'Take into Container':
                            found += f'<b>{source}</b> в <b>{e_time.split(" ", 1)[1][:5]}</b> положил в контейнер вещь (слот {info.split("Slot ", 1)[1]}) в измерении <b>{dim}</b>.\n\n'
                        else:
                            if info is not None and info != '':
                                found += f'<b>{source}</b> в <b>{e_time.split(" ", 1)[1][:5]}</b> совершил действие <b>{event}</b> (доп. инфо: {info}) в измерении <b>{dim}</b>.\n\n'
                            else:
                                found += f'<b>{source}</b> в <b>{e_time.split(" ", 1)[1][:5]}</b> совершил действие <b>{event}</b> в измерении <b>{dim}</b>.\n\n'
                        found_count += 1

                if found != '':
                    result += found
                    if (await bot.get_chat(message.chat.id)).type == 'private':
                        if found_count > 10:
                            file_name = f"Логи ({coords[0]} {coords[1]} {coords[2]}).html"
                            text = result

                            with open(file_name, 'w') as file:
                                file.write(text)

                            with open(file_name, 'rb') as file:
                                await message.reply_document(FSInputFile(file_name),
                                                             'В логах более 10-и действий, поэтому они были отправлены HTML-файлом. <b>Открой его в любом браузере.</b>')
                                os.remove(file_name)
                        else:
                            await message.reply(text=result)
                        #await message.answer(f'Пока что нет возможности узнать, какой предмет был взят из сундука/шалкера и т.п, а также логи представлены в общем виде и почти не меняются в зависимости от события. <b>В будущем это будет исправлено,</b> извини за неудобства.')

                    elif (await bot.get_chat(message.chat.id)).type == 'group' or (
                    await bot.get_chat(message.chat.id)).type == 'supergroup':
                        try:
                            if found_count > 10:
                                file_name = f"Логи ({coords[0]} {coords[1]} {coords[2]}).html"
                                text = result

                                with open(file_name, 'w', encoding="utf-8") as file:
                                    file.write(text)

                                with open(file_name, 'rb') as file:
                                    await bot.send_document(chat_id=message.from_user.id,
                                                            document=FSInputFile(file_name),
                                                            caption='В логах более 10-и действий, поэтому они были отправлены HTML-файлом. <b>Открой его в любом браузере.</b>')
                                    os.remove(file_name)
                            else:
                                await bot.send_message(message.from_user.id, text=result)
                            #await bot.send_message(message.from_user.id, f'Пока что нет возможности узнать, какой предмет был взят из сундука/шалкера и т.п, а также логи представлены в общем виде и почти не меняются в зависимости от события. <b>В будущем это будет исправлено,</b> извини за неудобства.')
                            await message.reply(
                                f'<b>Логи были отправлены тебе в ЛС</b>, чтобы не засорять чат.\n\n<b>Дата:</b> {date[:2]}.{date[3:]}\n<b>Координаты:</b> {coords[0]} {coords[1]} {coords[2]}')
                        except TelegramForbiddenError:
                            await message.reply(
                                f'<b>Отправь боту в ЛС /start и заново введи команду</b> (это можно сделать в личке бота), чтобы получить отчёт по логам.')
                else:
                    await message.reply(
                        f'Логи по координатам <b>{coords[0]} {coords[1]} {coords[2]}</b> за дату <b>{date[:2]}.{date[3:]}</b> не найдены.')
        elif message.text.count(' ') == 3:
            await message.reply(
                f'<b>Ты не ввёл дату!</b> Добавь её после координат в формате <code>/logs -256 64 0 31.01</code>.')
        else:
            await message.reply(
                f'<b>Команда введена неверно!</b> Требуемый формат: <code>/logs -256 64 0 31.01</code>.')


'''
