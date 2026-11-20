import telebot, time, requests
from telebot import types
from pprint import pformat

try: from utils import *
except Exception as e: input(e)

# Connecting to bot with API key
bot = telebot.TeleBot(bot_key, parse_mode='html', colorful_logs=True)

# Connecting to proxy
if connect_to_proxy:
    connect_proxy(bot)

# Starting message
log("BOTIK ACTIVATED")

# Log function
def logTG(message: types.Message, data: dict={}) -> None:
    if message.chat.id != owner_id:
        data["message text"] = message.text

        # Getting the name of the message sender
        name = message.from_user.first_name + (f' {message.from_user.last_name}' if message.from_user.last_name is not None else "")
        username = message.from_user.username
        ctime = dt.datetime.now()
        chat_type = message.chat.type
        chat_id = message.chat.id
        str_data = pformat(data, expand=True, sort_dicts=True) if len(data) else ""
        
        # Log message text
        bot.send_message(
            chat_id=owner_id,
            text=f'<pre>>> {ctime}\n   ({chat_type} - {chat_id})\n   [ {name} | @{username}]\n\n{str_data}</pre>'
        ) # Sending log message to the bot's owner

        time.sleep(1) # Sleeping for 1 second for some reason

# /start handler
@bot.message_handler(commands=["start", "help"])
def handle_start(message: types.Message):
    bot.send_message(message.chat.id, start_mesage) # Sending starting message to the user
    logTG(message) # Logging the message to the owner

# Buttons' markup
def get_buttons_markup(full_dz=False):
    buttons = types.InlineKeyboardMarkup(row_width=6)

    if full_dz:
        rel = types.InlineKeyboardButton("🔄", callback_data="reload_full")
        remove = types.InlineKeyboardButton(text="❌", callback_data="remove")
        buttons.add(rel, remove)
    else:
        rel = types.InlineKeyboardButton("🔄", callback_data="reload")
        remove = types.InlineKeyboardButton(text="❌", callback_data="remove")
        mon = types.InlineKeyboardButton("Пн", callback_data="0")
        tue = types.InlineKeyboardButton("Вт", callback_data="1")
        wed = types.InlineKeyboardButton("Ср", callback_data="2")
        thu = types.InlineKeyboardButton("Чт", callback_data="3")
        fri = types.InlineKeyboardButton("Пт", callback_data="4")
        sat = types.InlineKeyboardButton("Сб", callback_data="5")
        full = types.InlineKeyboardButton("📚", callback_data="full")
        buttons.add(mon, tue, wed, thu, fri, sat, full, rel, remove)

    return buttons


def send_dz(message: types.Message, chat_id: int | str, full_dz: bool):
    
    _, tomorrow = today_and_tomorrow() # orientating in time

    if not full_dz:
        bot.send_message(
            chat_id=chat_id,
            text=dz(tomorrow),
            reply_markup=get_buttons_markup()
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text=get_fulldz(), 
            reply_markup=get_buttons_markup(full_dz=True)
        )

    logTG(message) # Logging the message to the owner

#! /dz handler
@bot.message_handler(commands=["dz"])
def sendDZ(message: types.Message): 
    send_dz(message=message, chat_id=message.chat.id, full_dz=False)

#! /fuldz handler
@bot.message_handler(commands=["fulldz"])
def handle_start(message: types.Message):
    send_dz(message=message, chat_id=message.chat.id, full_dz=True)

#! Admin homework sending commands
@bot.message_handler(commands=["group_dz"])
def handle_start(message: types.Message): 
    send_dz(message=message, chat_id=main_group_id, full_dz=False)

@bot.message_handler(commands=["group_full"])
def handle_start(message: types.Message): 
    send_dz(message=message, chat_id=main_group_id, full_dz=True)

#! /consultations handler
@bot.message_handler(commands=["consultations"])
def hande_start(message: types.Message):
    bot.send_message(message.chat.id, "<b>КОНСУЛЬТАЦИИ</b>\n\n" + open(consultations_path, encoding="utf-8", mode="r").read().replace("\n\n\n", "\n\n")) # sending the list of all consultations
    logTG(message)

#! Callback handler
@bot.callback_query_handler(func=lambda c: True)
def callback(c: types.CallbackQuery):
    _, tomorrow = today_and_tomorrow() # Orientating in time
    
    # Reloading full dz message
    if c.data == "reload_full":
        bot.edit_message_text(
            chat_id=c.message.chat.id, 
            message_id=c.message.id, 
            text=get_fulldz(),
            reply_markup=get_buttons_markup(full_dz=True)
        )
    # Reloading dz message
    elif c.data == "reload":
        bot.edit_message_text(
            chat_id=c.message.chat.id, 
            message_id=c.message.id,
            text=dz(tomorrow),
            reply_markup=get_buttons_markup()
        )
    # Removing bot's message (owner only)
    elif c.data == 'remove':
        if c.json["from"]["id"] == owner_id:
            bot.delete_message(c.message.chat.id, c.message.id) # Deleting the message
    else:
        bot.send_message(
            text=get_fulldz() if c.data == "full" else dz(int(c.data)),
            chat_id=c.message.chat.id,
            receiver_user_id=c.from_user.id,
            callback_query_id=c.id,
        )

#! Meme handler
@bot.message_handler(commands=["meme"])
def message_handler(message: types.Message):

    # Setting up the main variables
    meme = get_random_meme()
    username = message.from_user.username
    user_data = get_user_data(username)
    user_data_path = f"users/{username}.json"
    meme_points = meme.level.generate_points()
    user_is_just_banned = False
    user_is_banned = time.time() < user_data["meme_ban_time"]

    # Meme logic
    if not user_is_banned:
        user_data["meme_points"] += meme_points
        user_data["last_meme_point"] = meme_points
        user_data["meme_ban_counter"] = user_data["meme_ban_counter"] + 1 if meme_points == 0 and meme_points == user_data["last_meme_point"] else 0
        user_data["meme_ban_time"] = 0

    if user_data["meme_ban_counter"] == meme_ban_limit:
        user_data["meme_ban_counter"] = 0
        user_data["meme_ban_time"] = time.time() + meme_ban_period
        user_is_just_banned = True

    # Saving user data
    json.dump(user_data, open(user_data_path, "r+"), indent=4)

    # Sending the message
    if user_is_just_banned or not user_is_banned:
        requests.post(
            apihelper.API_URL.format(bot_key, "sendPhoto"),
            data={
                "chat_id": message.chat.id,
                "has_spoiler": True,
                "reply_to_message_id": message.id,
                "caption": f"<b>@{message.from_user.username}</b> выбил мем редкости <span class=\"tg-spoiler\"><b>{meme.level_name}</b> {meme.level.emoji} (+{meme_points})</span>" \
                        + (f"<span class=\"tg-spoiler\">, а также <b>бан</b> на {meme_ban_period} секунд за получение нуля очков {meme_ban_limit} раз подряд! 🥳</span>" if user_is_just_banned else ""),
                "parse_mode": "html"
            },
            files = {"photo": meme.get_image()}
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            reply_to_message_id=message.id,
            text=f"@{username} будет находиться в мемном бане ещё {round(user_data["meme_ban_time"]-time.time())} секунд"
        )

    logTG(message, {"meme_path": meme.path, "meme_points": meme_points, "user_data": user_data})

@bot.message_handler(commands=["meme_top"])
def message_handler(message: types.Message):

    bot.send_message(
        chat_id=message.chat.id,
        text=get_meme_top_as_text()
    )

    logTG(message)


#! Any message handler
@bot.message_handler(func=lambda m: True)
def simple_answer(message: types.Message):

    # Admin message sending logic
    chat_id, *other_text = message.text.split("\n")
    if message.chat.id == owner_id and chat_id[1:].isdigit():
        bot.send_message(chat_id, "\n".join(other_text))

    # Answer to a swearing
    elif text_type(message.text) == "swearing" and "колеба" not in message.text.lower():
        
        name = message.from_user.first_name # Getting the user's name
        t = f'Внимание, {name}, пожалуйста, следите за своим лексиконом'
        reply_text = choice([
            'Уважаемый faggot, прошу следит за использованием нормативной лексики в чате класса.',
            f'Уважаемый {name}, пожалуйста, следить за свой лексикон, партия разочароваться ты, минус тысяча социальный кредит, минус кошка-жена.',
            'Про мать было лишнее...',
            t + ', иначе мне придётся передать всё Ирине Валерьевне.',
            t + ', а то уши вянут, хоть их у меня нет.',
            t + ', или мне придётся организовать свидание вашего рта с мылом.',
            t + ', спасибо за внимание.',
            t + ', не при детях же!',
            t + ', я не хочу разогревать свою аннигиляторную пушку.',
            None
        ])

        if reply_text is not None:
            bot.reply_to(message, reply_text) # Replying with text
        else:
            requests.post(
                apihelper.API_URL.format(bot_key, "sendPhoto"),
                data={
                    "chat_id": message.chat.id,
                    "reply_to_message_id": message.id,
                    "caption": f"Внимание, {message.from_user.first_name}, пожалуйста, следите за своим лексиконом.",
                    "parse_mode": "html"
                },
                files = {"photo": open(choice(swearing_pics_paths), 'rb')}
            )

            # bot.send_photo(
            #     message.chat.id, 
            #     photo=image,
            #     caption=f'Внимание, {message.from_user.first_name}, пожалуйста, следите за своим лексиконом.',
            #     reply_to_message_id=message.id
            # )

    elif find_word(message, ['фуу', "зараза"]):
        bot.reply_to(message, 'Вы быканули, или мне показалось? 🤨')

    # Answer to homework question
    elif text_type(message.text) == "dz_question":
        send_dz(message, "default")

    # Answer to "thank you"
    elif text_type(message.text) == "gratitude":
        name = message.from_user.first_name
        if name == "Роман": name = "сладенький"
        bot.reply_to(message, f'Всегда рад помочь, {name}!')

    # Answer to "sorry"
    elif text_type(message.text) == "sorry":
        bot.send_message(
            chat_id = message.chat.id, 
            reply_text = f'Не беспокойтесь, {message.from_user.first_name}, я не злопамятный.' + \
                        (f' Зачем мне помнить кучку пепла, оставшуюся после моей аннигиляторной пушки? 😃' if choice([0, 1]) else "")
        )

    elif text_type(message.text) == "cyber_vitya":
        bot.reply_to(message=message, text=ask_ai(message.text), parse_mode="html")

    logTG(message) # Logging the message to the owner

# Sticker handler
@bot.message_handler(content_types=["sticker"])
def handle_start(message):
    print(f'>> {dt.datetime.now()} -- [Sticker ID: {message.id}]')

# Bot polling
bot.infinity_polling(none_stop=True, timeout=200)
