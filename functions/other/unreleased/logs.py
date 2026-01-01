import asyncio
import os
import aiofiles

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv('token')
chat_id = os.getenv('chat_id')
logs_dir = os.getenv('logs_dir')

bot = Bot(token = bot_token, parse_mode = "html")
dp = Dispatcher()

offset = 0

async def on_startup():
    asyncio.create_task(read_logs())

async def read_logs():
    global offset
    async with aiofiles.open(logs_dir, mode='rb') as file:
        if offset == 0:
            await file.seek(0, 2)
            pos = await file.tell()
        while True:
            await file.seek(pos + offset, 0)
            line = await file.readline()
            if not line:
                await asyncio.sleep(0.01)
                continue
            else:
                offset += len(line)
                print(line.strip().decode('utf-8'))

dp.startup.register(on_startup)

async def main():
    await dp.start_polling(bot, on_startup = on_startup)

if __name__ == '__main__':
    asyncio.run(main())
