from aiogram.types import (
    #ReplyKeyboardMarkup,
    #KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

#from aiogram.utils.keyboard import ReplyKeyboardBuilder

rice_kb = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "Об игре", url = "https://telegra.ph/Gajd-po-mini-igre-v-bote-03-31"),
            InlineKeyboardButton(text = "× Закрыть", callback_data = 'close')
		}
	]
)

kb_close = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "× Закрыть", callback_data = 'delete')
		}
	]
)

kb_achs_back = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = u"‹ К списку", callback_data = 'to_list')
		}
	]
)