import os

from bot import bot
from tools.logger import log
from config import cfg
from Bot.Shop import keyboards
from lots_package import products_json, favorite_products
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B

from Bot.Payment import OrdersBotHandler, JSON_Orders
from .users import basefunc

from lots_package import delivery_products


class EchoFunctions:
    def __init__(self):
        self.cancel_text = '❌ Отменить'

    def open_category(self, call, category_id=None, from_arg=None):
        """
        Открывает категории. Если есть category_id, то открывает категорию с айди category_id, иначе выводит список категорий
        Если from_arg == 'favorite_lot', то считает, что категория открыта из меню избранного

        :param call:
        :param category_id:
        :param from_arg:
        :return:
        """
        user_id = call.message.chat.id
        bot.delete_message(user_id, call.message.message_id)
        try:
            if from_arg is not None and from_arg == 'favorite_lot':
                bot.send_message(user_id, f'*Выберите товар:*', parse_mode='Markdown',
                                 reply_markup=keyboards.keyboard_favorite_products(user_id))
                return True
            if not category_id:
                bot.send_message(chat_id=user_id, text='*Выберите товар:*', parse_mode='Markdown',
                                 reply_markup=keyboards.categories_all())
            else:
                basefunc.send_category(user_id, category_id)
            return True
        except Exception as e:
            log(f'Ошибка при получении списка товаров: {e}', lvl=2)
            return False

    def open_product(self, call, category_id, product_id, from_arg=None):
        """
        Открывает меню товара
        Если from_arg == 'favorite_lot', то считает, что товар был открыт из меню избранного

        :param call:
        :param category_id:
        :param product_id:
        :param from_arg:
        :return:
        """
        user_id = call.message.chat.id
        try:
            product = products_json.get_product(str(category_id), "id", str(product_id))
            if from_arg is not None and from_arg == 'favorite_menu':
                markup = keyboards.keyboard_favorite_product(category_id, product_id)
            else:
                markup = keyboards.product_keyboard(user_id, product_id, category_id)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if not product['image']:
                bot.send_message(chat_id=user_id, text=f'📃 *Товар:* {product["name"]}\n*💰 Цена:* '
                                                       f'{product["price"]} ₽\n*📃 Описание:* {product["description"]}\n📦 В наличии: {product["count"]}',
                                 parse_mode='Markdown', reply_markup=markup)
            else:
                bot.send_photo(user_id, product['image'],
                               caption=f'📃 *Товар:* {product["name"]}\n*💰 Цена:* '
                                       f'{product["price"]} ₽\n*📃 Описание:* {product["description"]}\n📦 *В наличии:* {product["count"]}',
                               parse_mode='Markdown', reply_markup=markup)
        except Exception as e:
            log(f'Ошибка при получении информации о товаре: {e}', lvl=2)
            return False

    def favorite_product(self, call, category_id, product_id, from_arg=None):
        """
        Выводит товар из меню избранного

        :param call:
        :param category_id:
        :param product_id:
        :param from_arg:
        :return:
        """
        user_id = call.message.chat.id
        try:
            if "delete_favorite" in call.data:
                favorite_products.delete_favorite_product(user_id, category_id, product_id)
                if 'from' in call.data and from_arg == 'favorite_menu':
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    bot.send_message(user_id, f'*✅ Товар успешно удалён из избранного! *', parse_mode='Markdown')
                    return
            product_id = product_id
            product = products_json.get_product(category_id, "id", product_id)
            markup_buy = K(row_width=5).add(
                *[B(text=i, callback_data=f'buy-lots_package={product_id}-count={i}') for i in
                  range(1, 11)]
            ).add(
                B(text='Назад', callback_data=f'from=favorite_product-to=favorite')
            ).add(B(text='🗑 Удалить из избранного',
                    callback_data=f'delete_favorite-cat={category_id}-prod={product_id}-from=favorite'))
            markup_buy.add(
                B('❌ Удалить товар', None,
                  f'func=delete_prod-cat={category_id}-prod={product_id}-from=prod_menu'))
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(chat_id=user_id, text=f'📃 *Товар:* {product["name"]}\n*💰 Цена:* '
                                                   f'{product["price"]} ₽\n*📃 Описание:* {product["description"]}',
                             parse_mode='Markdown', reply_markup=markup_buy)
            return
        except KeyError as e:
            log(f'eyError: {e}', lvl=2)
        except Exception as e:
            log(f'Ошибка при получении информации о товаре: {e}', lvl=2)

    def delete_prod(self, call, category, product, from_arg=None):
        """
        Удаляет лот

        :param call:
        :param category:
        :param product:
        :param from_arg:
        :return:
        """
        user_id = call.message.chat.id
        bot.send_message(user_id, f'⚠️*Удалить лот?*', parse_mode="Markdown",
                         reply_markup=K().row(
                             B('✅ Подтвердить', None, f'func=accept_delete_lot-cat={category}-prod={product}'),
                             B('❌ Отменить', None, f'func=cancel_delete_lot')
                         ))

    def accept_delete_lot(self, call, category, product):
        user_id = call.message.chat.id
        bot.delete_message(call.message.chat.id, call.message.message_id)
        products_json.delete_product(category, product)
        bot.send_message(user_id, f'✅ *Лот успешно удалён!*', parse_mode="Markdown")

    def cancel_delete_lot(self, call):
        bot.delete_message(call.message.chat.id, call.message.message_id)

    def add_favorite(self, call, category_id, product_id):
        """
        Добавляет лот в список избранного

        :param call:
        :param category_id:
        :param product_id:
        :return:
        """
        try:
            product_id = product_id
            user_id = call.message.chat.id
            add = favorite_products.save_favorite_product(user_id=user_id, category=category_id, product_id=product_id)

            if isinstance(add, str):
                bot.send_message(user_id, add, parse_mode='Markdown')
                return False

            if add:
                markup = keyboards.product_keyboard(user_id, product_id, category_id)
                bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=user_id,
                                              reply_markup=markup)
            else:
                bot.send_message(user_id, f'*❌ Товар* `{product_id}` *не добавлен в избранное!*',
                                 parse_mode='Markdown')
                return False
        except Exception as e:
            log(f'Ошибка при добавлении товара в избранное: {e}', lvl=2)
            return False

    def delete_favorite(self, call, category_id, product_id, from_arg=None):
        """
        Удаляет лот из избранного

        :param call:
        :param category_id:
        :param product_id:
        :param from_arg:
        :return:
        """
        user_id = call.message.chat.id
        favorite_products.delete_favorite_product(user_id, category_id, product_id)
        if from_arg is not None and from_arg == 'favorite_menu':
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, f'*✅ Товар успешно удалён из избранного! *', parse_mode='Markdown')
        else:
            markup = keyboards.product_keyboard(user_id, product_id=product_id, category_id=category_id)
            bot.edit_message_reply_markup(message_id=call.message.message_id, chat_id=user_id, reply_markup=markup)
        return

    def favorite(self, call):
        """
        Открывает меню лотов из меню изобранного

        :param call:
        :return:
        """
        user_id = call.message.chat.id
        try:
            favorites = favorite_products.get_favorite_products(user_id)
            favorite_products_keyboard = K(row_width=1).add(
                *[B(text=product["name"],
                    callback_data=f'func=favorite-prod={product["product_id"]}-cat={product["cat"]}')
                  for product in
                  favorites]
            ).add(
                B(text='🔙 Скрыть', callback_data='hide_keyboard')
            )
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, '*Избранные товары:*', parse_mode='Markdown',
                             reply_markup=favorite_products_keyboard)
        except Exception as e:
            log(f'Ошибка при получении списка избранных товаров: {e}', lvl=2)
            return False

    def categories_menu(self, call, from_arg=None):
        """
        Открывает меню всех категорий

        :param call:
        :param from_arg:
        :return:
        """
        user_id = call.message.chat.id
        try:
            bot.delete_message(user_id, call.message.message_id)
            categories = keyboards.categories_all(for_user=True if user_id not in cfg.ADMINS else False)
            if not categories:
                bot.send_message(user_id, '*🛒 Товаров нет*', parse_mode='Markdown')
                return
            bot.send_message(user_id, '*Выберите категорию:*', parse_mode='Markdown',
                             reply_markup=categories)
        except Exception as e:
            log(f'Ошибка при получении списка категорий: {e}', lvl=2)
            return False

    def favorite_lot(self, call, category_id, product_id, from_arg=None):
        """
        Открывает лот из избранного

        :param call:
        :param category_id:
        :param product_id:
        :param from_arg:
        :return:
        """
        user_id = call.message.chat.id
        try:
            product = products_json.get_product(category_id, "id", product_id)
            if not product:
                log(f'Товар с идентификатором {product_id} не существует', lvl=2)
                favorite_products.delete_favorite_product(user_id, category_id, product_id)
                bot.delete_message(user_id, call.message.message_id)
                bot.send_message(user_id, f'❌ *Товар не существует. Скорее всего он был удалён.*', parse_mode='Markdown')
                return
            if from_arg is not None and from_arg == 'favorite_menu':
                markup = keyboards.keyboard_favorite_product(category_id, product_id)
            else:
                markup = keyboards.product_keyboard(user_id, product_id, category_id)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if not product['image']:
                bot.send_message(chat_id=user_id, text=f'📃 *Товар:* {product["name"]}\n*💰 Цена:* '
                                                       f'{product["price"]} ₽\n*📃 Описание:* {product["description"]}\n📦 В наличии: {product["count"]}',
                                 parse_mode='Markdown', reply_markup=markup)
            else:
                bot.send_photo(call.message.chat.id, product['image'],
                               caption=f'📃 *Товар:* {product["name"]}\n*💰 Цена:* '
                                       f'{product["price"]} ₽\n*📃 Описание:* {product["description"]}\n📦 В наличии: {product["count"]}',
                               parse_mode='Markdown', reply_markup=markup)
        except Exception as e:
            log(f'Ошибка при получении информации о товаре: {e}', lvl=2)
            return False

    def delete_category(self, call, category, from_arg=None):
        """
        Удаляет категорию

        :param call:
        :param category:
        :param from_arg:
        :return:
        """
        chat_id = call.message.chat.id
        if not products_json.get_category(category_id=category):
            bot.delete_message(chat_id, call.message.message_id)
            bot.send_message(chat_id, f'*❌ Категория не существует*', parse_mode='Markdown')
            return
        M = K().row(B('✅ Подтвердить', None, f'func=accept_delete_category-cat={category}'),
                    (B('❌ Отменить', None, f'func=cancel_delete_category')))
        bot.send_message(chat_id, f'*Удалить категорию?*', parse_mode='Markdown', reply_markup=M)

    def cancel_delete_category(self, call):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        return

    def accept_delete_category(self, call, category):
        chat_id = call.message.chat.id
        del_cat = products_json.del_category(category=category)
        if not del_cat:
            bot.send_message(chat_id, f'*❌ Ошибка при удалении категории*', parse_mode='Markdown')
        else:
            bot.delete_message(chat_id, call.message.message_id)
            bot.send_message(chat_id, f"* 🗑 Категория удалена*", parse_mode='Markdown')

    def upload_products(self, call, category, product_id, bot_msg=None):
        chat_id = call.message.chat.id
        bot.register_next_step_handler(bot_msg := (bot.send_message(chat_id,
                                                                    f'*📁 Отправь мне товары, по 1 на каждую строку. \nЛибо txt файл*',
                                                                    parse_mode='Markdown',
                                                                    reply_markup=keyboards.cancel_keyboard)),
                                       self.upload_products_handler, category, product_id, bot_msg)

    def upload_products_handler(self, m, category, product_id, bot_msg):
        """
        Выгружает товары в товарный файл

        :param m:
        :param category:
        :param product_id:
        :param bot_msg:
        :return:
        """
        if m.text == self.cancel_text:
            bot.delete_message(m.chat.id, m.message_id)
            bot.delete_message(m.chat.id, bot_msg.message_id)
            bot.send_message(m.chat.id, "❌ Отменено", parse_mode='Markdown', reply_markup=keyboards.main_keyboard)
            return
        chat_id = m.chat.id
        if m.document:
            try:
                chat_id = m.chat.id
                if not m.document.mime_type.startswith('text/'):
                    if bot_msg:
                        bot.delete_message(chat_id, bot_msg.message_id)
                    bot.register_next_step_handler(
                        (bot_msg := bot.send_message(chat_id, "📌 *Отправь мне текстовый файл*.", parse_mode='Markdown',
                                                     reply_markup=keyboards.cancel_keyboard)),
                        self.upload_products_handler, category, product_id, bot_msg)
                file_path = bot.get_file(m.document.file_id).file_path
                downloaded_file = bot.download_file(file_path)
                with open((save_path := os.path.join(cfg.PRODUCT_PATH, f"{category}_temp.file")), 'wb') as new_file:
                    new_file.write(downloaded_file)
                with open(save_path, 'r') as f:
                    lines = list(map(str.strip, f.readlines()))
                os.remove(save_path)
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                return False
        else:
            lines = list(map(str.strip, m.text.split("\n")))
        upload = delivery_products.add_products(category, product_id, lines, absolut_add=True)
        if not upload:
            bot.send_message(chat_id, f'*❌ Ошибка при загрузке товаров*', parse_mode='Markdown')
            return False
        bot.send_message(chat_id, f'✅ *Успешно загружено* `{len(lines)}` *товаров*', parse_mode='Markdown')
        basefunc.send_product(chat_id, category, product_id)

    def buy(self, call, category, product, count: int):
        user_id = call.message.chat.id
        lot = products_json.get_product(str(category), "id", str(product))
        if int(lot['count']) < int(count):
            bot.send_message(chat_id=user_id, text=f'*❌ Недостаточно товаров в наличии*', parse_mode='Markdown')
            return False
        OrdersBotHandler.create_(user_id, category, product, int(count))

    def check_status_order(self, call, order):
        user_id = call.message.chat.id
        status = OrdersBotHandler.check_status_payment(order)
        if not status:
            bot.send_message(chat_id=user_id, text=f'*⌛️ Заказ не оплачен*',
                             parse_mode='Markdown')
            return False
        msg_id = call.message.message_id
        OrdersBotHandler.payed_order(user_id, order, msg_id)
        return True

    def cancel_order(self, call, order_id):
        try:
            chat_id = call.message.chat.id
            if JSON_Orders._status(chat_id, order_id):
                bot.send_message(chat_id, f'😎 *Заказ уже выполнен!*', parse_mode='Markdown')
                bot.edit_message_reply_markup(chat_id, message_id=call.message.message_id,
                                              reply_markup=K().add(B('✅ Заказ выполнен', None, 'decorate')))
                return False
            del_order = JSON_Orders.delete_order_(str(chat_id), order_id)
            if not del_order:
                bot.send_message(chat_id, f'*❌ Ошибка при отмене заказа*', parse_mode='Markdown')
                return False
            bot.edit_message_reply_markup(chat_id, message_id=call.message.message_id, reply_markup=K().add(B('❌ Заказ отменён', None, 'decorate')))
        except Exception as e:
            log(f'Ошибка при отмене заказа: {e}', lvl=2)
            return False

    def history_orders(self, call, count):
        user_id = call.message.chat.id
        orders = JSON_Orders._last_orders(str(user_id), int(count))
        if not orders:
            bot.send_message(chat_id=user_id, text=f'*❌ У вас нет заказов*', parse_mode='Markdown')
            return False
        msg = ""
        for order in orders:
            msg += f"🔑 *Название товара: *{order['name']}\n"
            msg += f"🆔 *Номер заказа: *{order['order_id']}\n"
            msg += f"📅 *Дата: *{order['time']}\n"
            msg += f"💶 *Сумма заказа: *{order['amount']} ₽\n\n"
        bot.send_message(chat_id=user_id, text=f'*📜 История заказов:*\n\n{msg}', parse_mode='Markdown', reply_markup=keyboards.hide_keyboard)




