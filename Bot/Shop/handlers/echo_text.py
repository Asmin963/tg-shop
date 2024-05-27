from bot import bot
from tools.logger import log
from telebot import types
from database import dbase
from config import cfg
from Bot.Shop import keyboards
from lots_package import products_json


@bot.message_handler(content_types=['text'])
def text_handler(m: types.Message):
    if m.text == '👤 Профиль':
        try:
            bot.delete_message(m.chat.id, m.message_id)
            user = dbase.get_user_column(m.from_user.id)
            bot.send_message(m.chat.id,
                             cfg.PROFILE_MESSAGE.format(user.user_id, user.username, user.register_date.split()[0], user.buys, user.balance),
                             parse_mode='Markdown', reply_markup=keyboards.profile_keyboard)
        except Exception as e:
            log(f'Ошибка при получении информации о пользователе: {e}', lvl=2)
    if m.text == '📖 Все категории':
        try:
            bot.delete_message(m.chat.id, m.message_id)
            categories = keyboards.categories_all(False if m.chat.id in cfg.ADMINS else True)
            if not categories:
                bot.send_message(m.chat.id, '*🛒 Товаров нет*', parse_mode='Markdown')
                return
            bot.send_message(m.chat.id, '*Выберите категорию:*', parse_mode='Markdown',
                             reply_markup=categories)
        except Exception as e:
            log(f'Ошибка при получении списка категорий: {e}', lvl=2)
    if m.text == '📄 Наличие товаров':
        try:
            bot.delete_message(m.chat.id, m.message_id)
            message = ""
            for category in products_json.get_categories():
                products = products_json.get_products(category['id'])
                if not products:
                    continue
                message += f"➖➖➖*{category['name']}*➖➖➖\n"
                products = products_json.get_products(category['id'])
                for product in products:
                    message += f"       *{product['name']} | {product['price']} ₽ | {product['count']} шт.*\n"
            if not message:
                message = '*🛒 Товаров нет*'
            bot.send_message(m.chat.id, message, parse_mode='Markdown')
        except Exception as e:
            log(f'Ошибка при получении списка товаров: {e}', lvl=2)
    if m.text == '🆘 Помощь':
        try:
            bot.delete_message(m.chat.id, m.message_id)
            bot.send_message(m.chat.id, cfg.HELP_MESSAGE, parse_mode='Markdown')
        except Exception as e:
            log(f'Ошибка при отправке сообщения поддержки: {e}', lvl=2)
    if m.text == '💎 О магазине':
        try:
            bot.delete_message(m.chat.id, m.message_id)
            bot.send_message(m.chat.id, cfg.ABOUT_MESSAGE, parse_mode='Markdown')
        except Exception as e:
            log(f'Ошибка при отправке сообщения информации о магазине: {e}', lvl=2)
    if m.text == '❌ Отменить':
        try:
            bot.delete_message(m.chat.id, m.message_id)
            bot.send_message(m.chat.id, cfg.START_MESSAGE, parse_mode='Markdown', reply_markup=keyboards.main_keyboard)
        except Exception as e:
            log(f'Ошибка при удалении сообщения: {e}', lvl=2)



