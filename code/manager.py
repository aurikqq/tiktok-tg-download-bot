from aiogram import Dispatcher

from modules.youtube import get_link
from modules.users import add_admin, add_user

dp = Dispatcher()

dp.register_message_handler(get_link, commands = ['yt'])
dp.register_message_handler(add_user, commands = ['user'])
dp.register_message_handler(add_admin, commands = ['admin'])