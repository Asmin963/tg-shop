from bot import bot
from tools.logger import log
from telebot import types
from database import dbase as sb
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B


def upload_products(call, category, product):
    user_id = call.message.chat.id
    bot.send_message(user_id, 'Добавить товар')


def edit_product(call, category, product):
    user_id = call.message.chat.id
    bot.send_message(user_id, 'Редактировать товар')


def send_product(call, category, product):
    user_id = call.message.chat.id
    bot.send_message(user_id, 'Выдать товар')

