from config import cfg
from telebot import TeleBot

token = cfg.TOKEN

if not token:
    raise Exception("Токен не найден")

bot = TeleBot(token)

