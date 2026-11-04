from utils import *
from pyperclip import copy
import re


def clear():
    print("\n"*50)

def remove_html_formatting(s: str) -> str:
    return "".join(re.split(r"</*.>", s))

def cmd_dz():
    _, tomorrow = today_and_tomorrow() # orientating in time
    homework = remove_html_formatting(dz(tomorrow).rstrip())
    print(homework)
    copy(homework)

def cmd_full_dz():
    homework = remove_html_formatting(get_fulldz())
    print(homework)
    copy(homework)

clear()
while True:
    print("\n\n[ dz | full_dz | exit ]")
    cmd = input("\n>> ")
    clear()
    match cmd:
        case "dz":
            cmd_dz()
        case "full_dz":
            cmd_full_dz()
        case "exit":
            exit(0)