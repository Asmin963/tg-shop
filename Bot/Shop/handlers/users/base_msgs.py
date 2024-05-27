from bot import bot
from lots_package import products_json
from config import cfg
from Bot.Shop import keyboards
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B



class BaseFunc:
    def __init__(self):
        pass

    def send_category(self, user_id, category_id):
        lot = products_json.get_category(category_id)
        m = keyboards.category_keyboard(category_id, user_id)
        if not lot["image"]:
            if user_id in cfg.ADMINS:
                m.add(B(text='➕ Добавить товар',
                        callback_data=f'func=add_lot_to_cat-cat={category_id}-from=add_lot_handler'))
            bot.send_message(chat_id=user_id,
                             text=f'*📃 Название:* {lot["name"]}\n*📃 Описание:* {lot["description"]}',
                             parse_mode='Markdown',
                             reply_markup=m)
        else:
            bot.send_photo(chat_id=user_id, photo=lot['image'],
                           caption=f'*📃 Название:* {lot["name"]}\n*📃 Описание:* {lot["description"]}',
                           parse_mode='Markdown', reply_markup=m)

    def send_product(self, user_id, category_id, product_id):
        product = products_json.get_product(category_id, product_id)
        markup = keyboards.product_keyboard(user_id, product_id, category_id)
        if not product['image']:
            bot.send_message(chat_id=user_id, text=f'📃 *Товар:* {product["name"]}\n*💰 Цена:* '
                                                   f'{product["price"]} ₽\n*📃 Описание:* {product["description"]}\n📦 В наличии: {product["count"]}',
                             parse_mode='Markdown', reply_markup=markup)
        else:
            bot.send_photo(user_id, product['image'],
                           caption=f'📃 *Товар:* {product["name"]}\n*💰 Цена:* '
                                   f'{product["price"]} ₽\n*📃 Описание:* {product["description"]}\n📦 *В наличии:* {product["count"]}',
                           parse_mode='Markdown', reply_markup=markup)
