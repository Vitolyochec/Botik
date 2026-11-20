import datetime as dt
from gigachat import GigaChat
from telebot import apihelper
from random import shuffle, choice
from tomllib import load as loadtoml
from os import listdir, mkdir
from winsound import Beep
import json


# Logging function
def log(msg: str):
    print(f'\n>> {dt.datetime.now()} -- {msg}')

# Config
try:    config = loadtoml(open(".config.toml", "rb")) # loading my config
except: config = loadtoml(open("config.toml", "rb"))  # loading config as downloaded project

bot_key = config["telegram_api_key"] # Telegram API key for bot
owner_id = config["owner_id"] # Telegram id of the bot's owner
owner_name = config["owner_name"] # Owner's account name
main_group_id = config["main_group_id"] # Class's group id
gigachat_api_key = config["gigachat_api_key"] # Gigachat API key
connect_to_proxy = config["connect_to_proxy"] # Whether to connect to proxies on start
apihelper.API_URL = config["API_URL"] + "/bot{0}/{1}" if config["API_URL"] != "" else apihelper.API_URL # API_URL throguh CloudFlare


# Paths
preambula_path = "data/preambula.txt"
birthdays_path = "data/birthdays.toml"
events_path = "data/events.toml"
word_bank_path = "data/word_bank.toml"
proxy_path = "data/proxy.txt"
consultations_path = "data/consultations.txt"
meme_levels_path = "data/meme_levels.toml"

must_directories = ["users", "memes"]

# Function to ask AI
gigachat = GigaChat(
    base_url="https://api.giga.chat/v1",
    credentials=gigachat_api_key,
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False,
    model = "GigaChat-2"
)

def ask_ai(user_prompt: str) -> str:
    answer = gigachat.chat(read_file(preambula_path) + user_prompt).choices[0].message.content.replace("GigaChat", "Кибер Витя").replace("**", "").replace("Сбер", "***")
    log(f"Asking Gigachat...\n\nQ:\n\n{user_prompt}\n\nA:\n\n{answer}\n\n\n")
    return answer 

# Word bank
word_bank = loadtoml(open(word_bank_path, "rb"))

# Birthdays dictionary
birthdays = loadtoml(open(birthdays_path, "rb"))

# Event dictionary
events = loadtoml(open(events_path, "rb"))

# List of homework files names
homework_files = ["monday.txt", "tuesday.txt", "wednesday.txt", "thursday.txt", "friday.txt", "saturday.txt"]

# List of signs
signs = '!,?.@№#"`()+-_=^:;~[]{}<>/|' + "'"

# List of swering pictures filepaths
swearing_pics_paths = ["pictures/" + x for x in listdir("pictures")]
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
        if read_file("homework/" + homework_files[x]) != '':
            for segment in read_file("homework/" + homework_files[x]).split("\n\n"):
                if isHomework(segment):    
                    fulldz += segment + "\n\n"
    return fulldz

# Function to get dz for tomorrow
def dz(day_num: int) -> str:
    today, _ = today_and_tomorrow()
    delta_day = 7 - (today - day_num) if today > day_num else day_num - today
    dz_text = formatted_date(delta_day)
    for segment in read_file("homework/" + homework_files[day_num]).split("\n\n"):
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

# Shuffles the given list and returns its shuffled variant
def shuffled(l: list) -> list:
    shuffle(l)
    return l

# Function to connect to one of the proxies in proxy.txt
best_proxies_num = 5
def connect_proxy(bot) -> None:
    apihelper.CONNECT_TIMEOUT = 100
    print("\nContecting proxy...\n")
    proxy_list = open(proxy_path).read().split()
    proxy_list = proxy_list[:best_proxies_num] + shuffled(proxy_list[best_proxies_num:])
    for proxy in proxy_list:
        print(f"[{proxy}]", end=" ")
        try:
            apihelper.proxy = {'https':f'socks5h://{proxy}'}
            # apihelper.proxy = {'https':f'https://long-pond-b143.irennasss3984.workers.dev/bot'}
            # print(apihelper.proxy)
            
            bot.get_me()
            print(f"- Connected")
            Beep(800, 500) # successfull beep
            with open(proxy_path, "w") as proxy_file:
                proxy_file.write("\n".join([proxy] + proxy_list[:proxy_list.index(proxy)] + proxy_list[proxy_list.index(proxy)+1:]))
            break
        except Exception as e:
            print(f"- Failed to connect - {e}")
    else:
        connect_proxy(bot)

# Meme utils

meme_ban_limit = 2
meme_ban_period = 10 * 60 # 10 minutes
medals = "🥇🥈🥉"

user_data_template = {
    "username": "",
    "meme_points": 0, 
    "meme_ban_time": 0,
    "last_meme_point": -1,
    "meme_ban_counter": 0
}

class MemeLevel:
    def __init__(self, emoji: str, points: list[int]):
        self.emoji = emoji
        self.points = points

    def generate_points(self) -> int:
        return choice(self.points)

# Loading meme levels
meme_levels = {}
for level, params in loadtoml(open(meme_levels_path, "rb")).items():
    meme_levels[level] = MemeLevel(params["emoji"], params["points"])

class Meme:
    def __init__(self, path: str):
        self.path = path
        self.level_name = path.split("/")[1].upper()
        self.level = meme_levels[self.level_name]

    def get_image(self):        
        return open(self.path, "rb")

def get_random_meme() -> Meme:
    
    memes = []
    for level in listdir("memes"):
        for meme_name in listdir(f"memes/{level}"):
            memes.append(f"memes/{level}/{meme_name}")

    meme_path = choice(memes)

    return Meme(meme_path)


def get_meme_top_as_text() -> str:

    users = sorted(
        [json.load(open("users/" + username, "rb")) for username in listdir("users")],
        key=lambda user: user["meme_points"],
        reverse=True
    )
    
    text = "<b>=====[МЕМ ТОП]=====</b>\n\n"

    for place in range(3):
        if place > len(users) - 1: break
        text += medals[place] + f"@{users[place]["username"]} - {users[place]["meme_points"]}\n"

    return text

def get_user_data(username: str) -> dict:

    user_data_path = f"users/{username}.json"

    # Trying to open the file or creating one if one does not exist
    try:    
        json.load(open(user_data_path, "rb"))
    except: 
        with open(user_data_path, "w") as file:
            file.write("{}")

    # User data table with default values
    user_data = user_data_template.copy()

    for key, val in json.load(open(user_data_path, "rb")).items():
        if key in user_data:
            user_data[key] = val

    user_data["username"] = username
    
    json.dump(user_data, open(user_data_path, "r+"), indent=4)
    
    return user_data

# Creating absent folders
for folder in must_directories: # Creating main folders
    if folder not in listdir():
        mkdir(folder)

for level in meme_levels.keys(): # Creating meme category folders
    if level not in listdir("memes/"):
        mkdir("memes/" + level)

# Bot /start message
start_mesage = (
    "Здравствуйте! Вас приветствует телеграмм бот по имени КиберВитя, созданный для ознакомления с домашним заданием.\nВот, что я могу:\n"
    "1) /dz - узнать домашнее задание\n"
    "2) /fuldz - полный список известного дз\n"
    "3) /consultation, /consultations - список консультаций на сегодня / неделю\n"
    "4) /check &ltслово&gt - проверка слова по словарю"
)