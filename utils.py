from enchant import Dict
import datetime as dt
from gigachat import GigaChat
from telebot import apihelper
from random import shuffle
from tomllib import load


# Config
try:    config = load(open(".config.toml", "rb")) # loading my config
except: config = load(open("config.toml", "rb"))  # loading config as downloaded project

bot_key = config["telegram_api_key"] # Telegram API key for bot
owner_id = config["owner_id"] # Telegram id of the bot's owner
owner_name = config["owner_name"] # Owner's account name
main_group_id = config["main_group_id"] # Class's group id
gigachat_api_key = config["gigachat_api_key"] # Gigachat API key
connect_to_proxy = config["connect_to_proxy"] # Whether to connect to proxies on start

# Paths
preambula_path = "data/preambula.txt"
birthdays_path = "data/birthdays.toml"
events_path = "data/events.toml"
word_bank_path = "data/word_bank.toml"
proxy_path = "data/proxy.txt"

# Dictionary
dictionary = Dict("ru_RU")

# Function to ask AI
gigachat = GigaChat(credentials=gigachat_api_key, verify_ssl_certs=False)

def ask_ai(user_prompt: str) -> str:
    answer = gigachat.chat(open(preambula_path, mode="r", encoding="utf-8").read() + user_prompt).choices[0].message.content.replace("GigaChat", "Кибер Витя").replace("**", "").replace("Сбер", "***")
    print(f">> {dt.datetime.now()} -- Asking Gigachat...\n\nQ:\n\n{user_prompt}\n\nA:\n\n{answer}\n\n\n")
    return answer 

# Word bank
word_bank = load(open(word_bank_path, "rb"))

# Birthdays dictionary
birthdays = load(open(birthdays_path, "rb"))

# Event dictionary
events = load(open(events_path, "rb"))

# List of homework files names
days = list(map(lambda x: x + ".txt", ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']))

# List of signs
signs = '!,?.@№#"`()+-_=^:;~[]{}<>/|' + "'"

# List of swering pictures filepaths
swearing_pics_paths = ['pictures/1.jpg', 'pictures/2.jpg']

# File reading function
def read_file(filename: str) -> str:
    return open(filename, encoding='utf-8', mode='r').read()

# Function for orientating in time
def today_and_tomorrow() -> int:
    today = dt.datetime.today().weekday()
    tomorrow = 0 if today == 5 or today == 6 else today + 1
    return today, tomorrow

# Date fromatter
month_to_emoji = {"12": "🎄", "01": "❄", "02": "📖", "03": "🌷", "04": "📖", "05": "📔", "06": "🌞", "07": "🌞", "08": "🌞", "09": "🍁", "10": "🍂", "11": "🌨"}
def formatted_date(delta_day: int) -> str:
    date = (dt.date.today() + dt.timedelta(days=delta_day)).__format__("%d.%m.%Y")
    if date[:5] in birthdays: 
        return f"<i>Дз на {date} - день рождения {birthdays[date[:5]]}</i> 🥳\n\n" # Birthday variant
    return f"<i>Дз на {date}</i> {month_to_emoji[date[3:5]]}\n\n"
    

# No homework for a subject checker
def isHomework(segment: str) -> bool:
    if len(segment) == 0: # checking for an empty string
        return False
    if segment.rstrip()[-1] == "-": # checking for a "-" situation in the end
            return False
    return True

# Function to get full dz text
def get_fulldz() -> str:
    _, tomorrow = today_and_tomorrow() # Orientating in time
    fulldz = '<i>Дз на неделю 📚</i>\n\n' # Variable for full dz text
    # Iterating over all dz files and adding dz to the fulldz variable
    for i in range(6):
        x = tomorrow + i - 6 if tomorrow + i > 5 else tomorrow + i
        if read_file("homework/" + days[x]) != '':
            for segment in read_file("homework/" + days[x]).split("\n\n"):
                if isHomework(segment):    
                    fulldz += segment + "\n\n"
    return fulldz

# Function to get dz for tomorrow
def dz(day_num: int) -> str:
    today, _ = today_and_tomorrow()
    delta_day = 7 - (today - day_num) if today > day_num else day_num - today
    dz_text = formatted_date(delta_day)
    for segment in read_file("homework/" + days[day_num]).split("\n\n"):
        if isHomework(segment):
            dz_text += segment + "\n\n"
    
    date = (dt.date.today() + dt.timedelta(days=delta_day)).__format__("%d.%m.%Y")
    if date[:5] in events:
        dz_text += f"<b>⚠ ВАЖНОЕ СОБЫТИЕ [{date[:5]}]: ⚠</b>\n<b>{events[date[:5]]}</b>"
    return dz_text

# Container working functions
def check_container(container: list, message) -> bool:
    for item in container:
        if item in message.text.lower():
            return True
    return False

def find_word(message, wordList: list) -> bool:
    message_text = message.text.lower() # Getting the message text
    for sign in signs: # Removing all the non-letter characters
        message_text = message_text.replace(sign, ' ')
    message_text = ' ' + message_text + ' '
    for word in wordList: # Checking if the message text contains the word
        if word in message_text:
            return True
    return False

# Function to identify the type of the message
def text_type(text: str) -> str:
    text = text.lower()
    while "  " in text: text = text.replace("  ", " ") # removing extra spaces
    for sign in signs: text = text.replace(sign, " ")  # removing all the unnecessary signs
    word_list = text.split()  # making a list of the words
    for group_name, group in word_bank.items():  # iterating over the groups
        for root in group["contains"]:  # checking for the roots
            if root.lower() in text:
                return group_name
        for word in group["equal"]:  # checking for the words
            if word.lower() in word_list:
                return group_name

# Function to connect to one of the proxies in proxy.txt
def connect_proxy(bot):
    print("\nContecting proxy...\n")
    proxy_list = open(proxy_path).read().split()
    proxy_list = proxy_list[:3] + shuffle(proxy_list[3:])
    for proxy in proxy_list:
        try:
            apihelper.proxy = {'https':f'socks5h://{proxy}'}
            bot.get_me()
            print(f"Proxy connected [{proxy}]")
            with open(proxy_path, "w") as proxy_file:
                proxy_file.write("\n".join([proxy] + proxy_list[:proxy_list.index(proxy)] + proxy_list[proxy_list.index(proxy)+1:]))
            break
        except:
            print(f"Failed to connect to [{proxy}]")
    else:
        connect_proxy(bot)

# Bot /start message
start_mesage = (
    "Здравствуйте! Вас приветствует телеграмм бот по имени КиберВитя, созданный для ознакомления с домашним заданием.\nВот, что я могу:\n"
    "1) /dz - узнать домашнее задание\n"
    "2) /fuldz - полный список известного дз\n"
    "3) /consultation, /consultations - список консультаций на сегодня / неделю\n"
    "4) /check &ltслово&gt - проверка слова по словарю"
)