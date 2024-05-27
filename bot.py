from config import cfg
from telebot import TeleBot

token = cfg.TOKEN

if not token:
    raise Exception("Токен не найден")

if not cfg.ADMINS:
    raise Exception("Администраторы не найдены")

bot = TeleBot(token)

