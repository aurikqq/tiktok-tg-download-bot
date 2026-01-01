from aiogram.types import Message

import bot

async def add_admin(message: Message):
    id = int(message.text.split[1])
    bot.allowlist[id] = 'admin'
    await message.reply(f"Юзер с ID {id} добавлен в список админов.")

async def add_user(message: Message):
    id = int(message.text.split[1])
    bot.allowlist[id] = 'user'
    await message.reply(f"Юзер с ID {id} добавлен в список админов.")