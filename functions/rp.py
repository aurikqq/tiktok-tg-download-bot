from aiogram.types import Message

async def act(message: Message):
        full_name = message.from_user.full_name

        if (message.reply_to_message != None):
            reply_full_name = message.reply_to_message.from_user.full_name
        else:
            reply_full_name = None

        if message.text[:len('!обнять')] == '!обнять':
            act_command = '!обнять'
            act_message = 'обнял(а)'
            act_emoji = '🫂'
        elif message.text[:len('!укусить')] == '!укусить':
            act_command = '!укусить'
            act_message = 'укусил(а)'
            act_emoji = '😖'
        elif message.text[:len('!сжечь')] == '!сжечь':
            act_command = '!сжечь'
            act_message = 'сжёг(ла)'
            act_emoji = '🔥'
        elif message.text[:len('!убить')] == '!убить':
            act_command = '!убить'
            act_message = 'убил(а)'
            act_emoji = '☠️'
        elif message.text[:len('!ударить')] == '!ударить':
            act_command = '!ударить'
            act_message = 'ударил(а)'
            act_emoji = '👊'
        elif message.text[:len('!поцеловать')] == '!поцеловать':
            act_command = '!поцеловать'
            act_message = 'поцеловал(а)'
            act_emoji = '😘'
        elif message.text[:len('!похоронить')] == '!похоронить':
            act_command = '!похоронить'
            act_message = 'похоронил(а)'
            act_emoji = '⚰️'
        elif message.text[:len('!ядерка')] == '!ядерка':
            act_command = '!ядерка'
            act_message = 'сбросил(а) ядерку на'
            act_emoji = '☢️'
        elif message.text[:len('!послать')] == '!послать':
            act_command = '!послать'
            act_message = 'послал(а)'
            act_emoji = '🤬'
        elif message.text[:len('!погладить')] == '!погладить':
            act_command = '!погладить'
            act_message = 'погладил(а)'
            act_emoji = '✋'
        elif message.text[:len('!покормить')] == '!покормить':
            act_command = '!покормить'
            act_message = 'покормил(а)'
            act_emoji = '😋'
        elif message.text[:len('!чай')] == '!чай':
            act_command = '!чай'
            act_message = 'пошёл(ла) пить чай с'
            act_emoji = '☕️'
        elif message.text[:len('!кофе')] == '!кофе':
            act_command = '!кофе'
            act_message = 'пошёл(ла) пить кофе с'
            act_emoji = '☕️'
        elif message.text[:len('!пригласитьчай')] == '!пригласитьчай':
            act_command = '!пригласитьчай'
            act_message = 'пригласил(а) на чай'
            act_emoji = '👀'
        elif message.text[:len('!пригласитькофе')] == '!пригласитькофе':
            act_command = '!пригласитькофе'
            act_message = 'пригласил(а) на кофе'
            act_emoji = '☕️'
        elif message.text[:len('!съесть')] == '!съесть':
            act_command = '!съесть'
            act_message = 'съел(а)'
            act_emoji = '😋'
        elif message.text[:len('!бухать')] == '!бухать':
            act_command = '!бухать'
            act_message = 'пошёл(ла) бухать с'
            act_emoji = '🍾'
        elif message.text[:len('!трахнуть')] == '!трахнуть':
            act_command = '!трахнуть'
            act_message = 'трахнул(а)'
            act_emoji = '🔞'
            
        if message.text[:len(act_command)] == act_command:
            if len(message.text) > len(act_command) and message.reply_to_message == None:
                arg = message.text.split(' ', 1)[1]
                await message.answer(f'<b><a href="tg://user?id={message.from_user.id}">{full_name}</a> {act_message} {arg} {act_emoji}</b>')
                await message.delete()
            elif len(message.text) == len(act_command) and message.reply_to_message == None:
                await message.reply(f'Ответь командой на сообщение другого пользователя или напиши что-то после неё.')
            else:
                await message.answer(f'<b><a href="tg://user?id={message.from_user.id}">{full_name}</a> {act_message} <a href="tg://user?id={message.reply_to_message.from_user.id}">{reply_full_name}</a> {act_emoji}</b>')
                await message.delete()

async def me(message: Message):
    full_name = message.from_user.full_name
    
    if len(message.text) > len('/me'):
        text = message.text.split(' ', 1)[1] 
        await message.answer(f'<b><a href="tg://user?id={message.from_user.id}">{full_name}</a> {text}</b>')
        await message.delete()
    else:
        await message.answer('<b>Введи текст после /me, чтобы сделать что-то.</b>\n\nПример: <code>/me написал команду</code>.')
    