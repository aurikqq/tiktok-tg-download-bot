from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup, 
    WebAppInfo
)

from aiogram.utils.keyboard import ReplyKeyboardBuilder

kb_edit = ReplyKeyboardMarkup(
	keyboard = [
		[
			KeyboardButton(text = "Имя"),
            KeyboardButton(text = "Ник"),
            KeyboardButton(text = "Возраст")
		],
        [
            KeyboardButton(text = "Пол"),
            KeyboardButton(text = "Страна"),
            KeyboardButton(text = "Дата рождения")
        ],
        [
            KeyboardButton(text = "Дата присоединения"),
            KeyboardButton(text = "Описание"),
            KeyboardButton(text = "Удалить профиль")
        ],
        [
            KeyboardButton(text = "Отмена")    
        ]
	],
    resize_keyboard = True,
    one_time_keyboard = True,
    input_field_placeholder = "Что изменить в профиле?",
    selective = True,
    row_width = 3
)

kb_ip = ReplyKeyboardMarkup(
	keyboard = [
		[
			KeyboardButton(text = "Добавить IP", web_app = WebAppInfo(url = 'https://aurikqq.github.io/poip.github.io/'))
		],

	],
    resize_keyboard = True,
    one_time_keyboard = True,
    input_field_placeholder = "Жди админов у себя дома...",
    selective = True,
)

kb_idea_rate = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "✅ Одобрить", callback_data = 'idea_rate_approve'),
		},
        {
            InlineKeyboardButton(text = "❌ Отклонить", callback_data = 'idea_rate_dismiss'),
        },
        {
            InlineKeyboardButton(text = "🚫 Уменьшить репутацию", callback_data = 'idea_rate_punish'),
        },
        {
            InlineKeyboardButton(text = "💬 Отправить игрокам", callback_data = 'idea_rate_send'),
        },
        {
            InlineKeyboardButton(text = "‹ Отмена", callback_data = 'idea_rate_cancel'),    
        }
	],
)

kb_idea_menu = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "Оценить идею", callback_data = 'idea_rate'),
            InlineKeyboardButton(text = "Переименовать", callback_data = 'idea_rename'),
		},
        {
           InlineKeyboardButton(text = "‹ Отмена", callback_data = 'idea_cancel'), 
        }
	],
)

kb_edition = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "Java", callback_data = 'java'),
            InlineKeyboardButton(text = "Bedrock", callback_data = 'bugrock'),
		},
        {
           InlineKeyboardButton(text = "Оба", callback_data = 'both'), 
        }
	],
)


kb_city_continiue = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "› Продолжить", callback_data = 'city_continue')
		}
	],
)

kb_city_cancel = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "× Отменить", callback_data = 'city_cancel')
		}
	],
)

kb_city_confirm = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "✅ Всё верно", callback_data = 'right'),
			InlineKeyboardButton(text = "⚙️ Изменить", callback_data = 'change')
		}
	],
)

kb_city_edit = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "Название", callback_data = 'city_name'),
			InlineKeyboardButton(text = "Жители", callback_data = 'city_citizens'),
			InlineKeyboardButton(text = "Координаты", callback_data = 'city_coords'),
		},
        {
			InlineKeyboardButton(text = "‹ Назад", callback_data = 'city_back')
		}
	],
)



kb_back = InlineKeyboardMarkup(
	inline_keyboard = [
        {
			InlineKeyboardButton(text = "‹ Назад", callback_data = 'back')
		}
	],
)

kb_city_edit_back = InlineKeyboardMarkup(
	inline_keyboard = [
        {
			InlineKeyboardButton(text = "‹ Назад", callback_data = 'city_edit_back')
		}
	],
)


kb_countries_1 = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "Беларусь 🇧🇾", callback_data = "BY"),
			InlineKeyboardButton(text = "Украина 🇺🇦", callback_data = "UA"),
		},
        {
            InlineKeyboardButton(text = "Россия 🇷🇺", callback_data = "RU"),
			InlineKeyboardButton(text = "Казахстан 🇰🇿", callback_data = "KZ"),
            
		},
        {
           InlineKeyboardButton(text = "➡️", callback_data = 'next'), 
           InlineKeyboardButton(text = "❌", callback_data = 'close'), 
        }
	],
)
kb_countries_2 = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "Швеция 🇸🇪", callback_data = "SE"),
            InlineKeyboardButton(text = "Узбекистан 🇺🇿", callback_data = "UZ"),
		},
        {
            InlineKeyboardButton(text = "Азербайджан 🇦🇿", callback_data = "AZ"),
			InlineKeyboardButton(text = "Германия 🇩🇪", callback_data = "DE"),
            #InlineKeyboardButton(text = "Очко Юры", callback_data = 'ass'),
		},
        {
           InlineKeyboardButton(text = "⬅️", callback_data = 'back'),
           InlineKeyboardButton(text = "❌", callback_data = 'close'),
        }
	],
)
kb_country = InlineKeyboardMarkup(
    inline_keyboard = [
        {
           InlineKeyboardButton(text = "⬅️", callback_data = 'back'),
           InlineKeyboardButton(text = "❌", callback_data = 'close'), 
        }
	],
)

kb_close = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "× Закрыть", callback_data = 'delete'),
		}
	]
)

kb_help = InlineKeyboardMarkup(
	inline_keyboard = [
        {
            InlineKeyboardButton(text = "Чат", callback_data = 'help_chat'),
            InlineKeyboardButton(text = "Сервер", callback_data = 'help_server'),
            InlineKeyboardButton(text = "Бот", callback_data = 'help_bot'),
		},
		{
			InlineKeyboardButton(text = "Создатели бота", callback_data = 'help_credits'),
		}
	]
)

kb_skip = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "Пропустить", callback_data = 'skip'),
		}
	]
)

kb_menu = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "Меню", callback_data = 'menu'),
		}
	]
)

kb_cancel = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "Отменить", callback_data = 'cancel'),
		}
	]
)

valentine_take = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "Забрать", callback_data = 'valentine'),
		}
	]
)

def yes_no():
    items = [
        "Да",
        "Нет"
        ]
    builder = ReplyKeyboardBuilder()
    [builder.button(text = item) for item in items]
    return builder.as_markup(resize_keyboard = True, one_time_keyboard = True, input_field_placeholder = "Выбери вариант", selective = True)

""" заготовка для клавиатуры из гайда
links_kb = InlineKeyboardMarkup(
	inline_keyboard = [
		{
			InlineKeyboardButton(text = "тест", url = "https://google.com"),
			InlineKeyboardButton(text = "тест 2", url = "tg://resolve?domain=aurikqq")
		}
	]
)
"""