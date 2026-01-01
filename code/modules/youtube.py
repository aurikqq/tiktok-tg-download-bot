from aiogram import Bot
from aiogram.types import Message, FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from pytubefix import YouTube

token = '7924001209:AAGdhtUa-C-YHs0XFyB0BPY4GV2LVDmSL9g'

bot = Bot(token, default = DefaultBotProperties(parse_mode = ParseMode.HTML))
    
async def get_link(message: Message):
    if (message.text != '/yt'):
        if ("youtu" in message.text):
            global resp
            resp = await message.reply("Секунду...")
            yt = YouTube(message.text)
            stream = yt.streams.get_highest_resolution()
            file = stream.download()
            input_file = FSInputFile(file)
            await bot.send_video(message.chat.id, input_file)
            await message.answer(f"<b>Готово!</b> Видео \"{stream.title}\" загружено.")
            await resp.delete()
        else:
            await message.reply("<b>Отправь ссылку на видео</b>, а не текст.")
    else:
        await message.reply("<b>Отправь ссылку</b> на видео с Ютуба вместе с командой - например, youtube.com/somevideo")
        
async def on_progress(stream, chunk, file_handle, bytes_remaining):
    filesize = stream.filesize
    bytes_received = filesize - bytes_remaining
    edited_text = f"Секунду...\nЗагружено {bytes_received} байт из {filesize}."
    await resp.edit_text(edited_text)
