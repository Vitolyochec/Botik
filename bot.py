import math, random, telebot, time
from telebot import types
from utils_and_config import *

# Connecting to bot with API key
bot = telebot.TeleBot(bot_key, parse_mode='html')

# Connecting to proxy
connect_proxy(bot)

# Starting message
print(f'\n>> {dt.datetime.now()} -- BOT STARTED')

# Log function
def log(message):
    if message.chat.id != owner_id:
        # print(message)
        # Getting the name of the message sender
        name = message.from_user.first_name
        if message.from_user.last_name is not None:
            name += f' {message.from_user.last_name}' # Getting sender's name if exists
        
        # Log message text
        text = f'>> {dt.datetime.now()}\n     [{message.chat.type} - {message.chat.id}]\n     {name}:\n<b>{message.text}</b>' 
        bot.send_message(owner_id, text=text) # Sending log message to the bot's owner

        time.sleep(2) # Sleeping for 2 seconds for some reason

# /start handler
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.send_message(message.chat.id, start_mesage) # Sending starting message to the user
    log(message) # Logging the message to the owner

# Buttons' markup
def get_buttons_markup(full_dz=False):
    buttons = types.InlineKeyboardMarkup(row_width=6)

    if full_dz:
        rel = types.InlineKeyboardButton("🔄 Обновить", callback_data="reload_full")
        remove = types.InlineKeyboardButton(text="❌ Убрать нафиг", callback_data="remove")
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

#! /dz handler

def send_dz(message, send_mode: str):
    
    _, tomorrow = today_and_tomorrow() # orientating in time

    # Sending the message
    bot.send_message(
        chat_id=main_group_id if send_mode == "main_group" else message.chat.id,
        text=dz(tomorrow),
        reply_markup=get_buttons_markup() # Getting the buttons for the message
    )

    log(message) # Logging the message to the owner

@bot.message_handler(commands=["дз", "dz"])
def sendDZ(message): 
    send_dz(message, message.chat.type)
    
@bot.message_handler(commands=["group", "группа"])
def handle_start(message): 
    send_dz(message, "main_group")

#! /fuldz handler

last_full_dz_message = [0, 0] # Last full dz message variable

@bot.message_handler(commands=["фулдз", "fuldz"])
def handle_start(message):

    # Deleting the previous message to keep the chat cleaner and to avoid most of spamming
    if message.chat.type == "group" and last_full_dz_message[0] != 0 and last_full_dz_message[1] != 0:
        bot.delete_message(last_full_dz_message[0], last_full_dz_message[1])

    # Sending the full dz message
    sent_message = bot.reply_to(
        message, 
        text=get_fulldz(), 
        reply_markup=get_buttons_markup(full_dz=True)
    )
    last_full_dz_message[0], last_full_dz_message[1] = sent_message.chat.id, sent_message.id # Saving the data of the last sent full dz message
    log(message) # Logging the message to the owner

# /fooldz handler
@bot.message_handler(commands=["fool", "fooldz"])
def handle_start(message):
    bot.reply_to(message, "Fool - с английского дурак, а я не такой. Не обзывайте меня, позязя 😥") # Replying to the message
    log(message) # Logging the message to the owner

#! /check handler
@bot.message_handler(commands=["check", "проверь", "проверить"])
def handle_start(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Нечего чекать, дурында -_-"); return 0
    
    word = message.text.split()[1]

    if dictionary.check(word):
        bot.reply_to(message, f'Да, есть такое слово <i><b>"{word}".</b></i>')
    else:
        bot.reply_to(message, f'Извините, но, возможно, вы имели в виду что-то из этого:\n' + "<i><b>" + ', '.join(dictionary.suggest(word)) + "</b></i>")

#! /consultations handler

@bot.message_handler(commands=["consultations", "консультации"])
def hande_start(message):
    bot.send_message(message.chat.id, "<b>КОНСУЛЬТАЦИИ</b>" + open("consultations.txt", encoding="utf-8", mode="r").read().replace("\n\n\n", "\n\n")) # sending the list of all consultations
    log(message)

# /consultation button layout
def consultaion_markup(today):
    next = types.InlineKeyboardButton(text="▶", callback_data=f"next{today}")
    prev = types.InlineKeyboardButton(text="◀", callback_data=f"prev{today}")
    markup = types.InlineKeyboardMarkup()
    markup.add(prev, next)
    return markup

#! /consultation handler
@bot.message_handler(commands=["consultation", "консультация"])
def handle_start(message):
    today, _ = today_and_tomorrow()
    bot.send_message(
        message.chat.id, open("consultations.txt", encoding="utf-8", mode="r").read().split("\n\n\n")[today if today < 5 else 0], 
        reply_markup=consultaion_markup(today if today < 5 else 0),
        )

#! Callback handler
@bot.callback_query_handler(func=lambda c: True)
def callback(c: telebot.types.CallbackQuery):
    _, tomorrow = today_and_tomorrow() # Orientating in time

    # Changing consultation list
    if c.data[:-1] in ["next", "prev"]:
        day = int(c.data[-1])
        next_day = day-1 if c.data[:-1] == "prev" else day+1
        if next_day < 0: next_day = 4
        if next_day > 4: next_day = 0

        bot.edit_message_text(
            chat_id=c.message.chat.id, 
            message_id=c.message.id,
            text=open("consultations.txt", encoding="utf-8", mode="r").read().split("\n\n\n")[next_day],
            reply_markup=consultaion_markup(next_day)
        )
    # Reloading full dz message
    elif c.data == "reload_full":
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
        bot.delete_message(c.message.chat.id, c.message.id) # Deleting the message
    else:
        sent_message = bot.send_message(
            text=get_fulldz() if c.data == "full" else dz(int(c.data)),
            chat_id=c.message.chat.id,
            receiver_user_id=c.from_user.id,
            callback_query_id=c.id,
        )
        log(sent_message) # Logging the message for the owner

#! Any message handler
@bot.message_handler(func=lambda m: True)
def simple_answer(message):

    # Admin message sending logic
    chat_id, *other_text = message.text.split("\n")
    if message.chat.id == owner_id and str(abs(int(chat_id))).isdigit():
        bot.send_message(chat_id, "\n".join(other_text))

    # Answer to a swearing
    elif text_type(message.text) == "swearing" and 'колеба' not in message.text.lower():
        x = random.randint(1, 10)
        name = message.from_user.first_name # Getting user's name
        reply_text = f'Внимание, {name}, пожалуйста, следите за своим лексиконом'
        image = ''
        match x:
            case 1: reply_text  = 'Уважаемый faggot, прошу следит за использованием нормативной лексики в чате класса.'
            case 2: reply_text += ', иначе мне придётся передать всё Ирине Валерьевне.'
            case 3: reply_text += ', а то уши вянут, хоть их у меня нет.'
            case 4: reply_text += ', или мне придётся организовать свидание вашего рта с мылом.'
            case 5: reply_text = f'Уважаемый {name}, пожалуйста, следить за свой лексикон, партия разочароваться ты, минус тысяча социальный кредит, минус кошка-жена.'
            case 6: reply_text += ', спасибо за внимание.'
            case 7: reply_text += ', не при детях же!'
            case 8: reply_text += ', я не хочу разогревать свою аннигиляторную пушку.'
            case 9: reply_text = 'Про мать было лишнее...'
            case 10: image = open(swearing_pics[random.randint(0, len(swearing_pics)-1)], 'rb') # Choosing random swearing picture
        if image == '':
            bot.reply_to(message, reply_text) # Replying with text
        else: # Relpying with an image
            bot.send_photo(
                message.chat.id, 
                photo=image,
                caption=f'Внимание, {message.from_user.first_name}, пожалуйста, следите за своим лексиконом.',
                reply_to_message_id=message.id
            )
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
        name = message.from_user.first_name # Getting user's name
        reply_text = f'Не беспокойтесь, {name}, я не злопамятный.'
        if name == owner_name:
            reply_text += f' Зачем мне помнить кучку пепла, оставшуюся после моей аннигиляторной пушки? 😃'
        bot.send_message(message.chat.id, reply_text)
    elif text_type(message.text) == "cyber_vitya" and message.from_user.username != "Jrnrndnnf":
        bot.reply_to(message, text=ask_ai(message.text), parse_mode="html")

    log(message) # Logging the message to the owner

# Sticker handler
@bot.message_handler(content_types=["sticker"])
def handle_start(message):
    print(f'--[Sticker ID: {message.id}]--')

# Bot polling
bot.infinity_polling(none_stop=True, timeout=120)