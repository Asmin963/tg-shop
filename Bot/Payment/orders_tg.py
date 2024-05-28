from datetime import datetime, timedelta

from lots_package import products_json

from lots_package import delivery_products
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
from tools.logger import log
from config import cfg
import time
from Bot.Shop import keyboards
from bot import bot
from database import dbase as db
from Bot.Shop.handlers.users import basefunc

from .orders_json import OrderManagerJSON

JSON_Orders = OrderManagerJSON(cfg.ORDERS_PATH)


class OrdersBotMessageHandler:
    def __init__(self):
        pass

    def create_(self, user_id, category, product_id, count: int = 1, from_balance=False):
        """
        Создает заказ на оплату

        :param user_id:
        :param category:
        :param product_id:
        :param count:
        :return:
        """
        lot = products_json.get_product(str(category), "id", str(product_id))
        amount = int(lot['price']) * count
        if int(db.get_user_column(user_id, 'balance')) < amount and amount > 1:
            amount -= int(db.get_user_column(user_id, 'balance'))
            from_balance = True
        if not lot:
            bot.send_message(user_id, f'*❌ Такого товара не существует*', reply_markup=keyboards.main_keyboard,
                             parse_mode="Markdown")
            log(f'Пользователь {user_id} пытался купить несуществующий товар {product_id}', lvl=4)
            time.sleep(1)
            basefunc.send_category(user_id, category)
            return False

        product = products_json.get_product(category, "id", str(product_id))
        add_ord = JSON_Orders.add_order(user_id, category, product_id, product['name'],
                                        product['price'], count, time.strftime("%Y-%m-%d %H:%M:%S"),
                                        amount, desc=f'Заказ из @{bot.get_me().username}\nТовар: {product["name"]}')
        if not add_ord:
            log(f'Ошибка при добавлении заказа')
            return False
        bot.send_message(user_id, cfg.ORDER_MESSAGE.format(
            add_ord.name, add_ord.price, add_ord.quantity, add_ord.order_id, add_ord.time, add_ord.amount, (datetime.now() + timedelta(minutes=15)).strftime('%H:%M')
        ), reply_markup=keyboards.order_keyboard(add_ord.order_id, add_ord.amount, add_ord.lang, add_ord.currency, add_ord.desc))
        if from_balance:
            db.add_money_user(user_id, -int(db.get_user_column(user_id, 'balance')))
        return True

    def payed_order(self, user_id, order_id, msg_id=None):
        order_ = JSON_Orders.get_orders_by_user_id(user_id, order_id)
        if not order_:
            log(f'Пользователь {user_id} пытался оплатить несуществующий заказ {order_id}', lvl=4)
            return False
        product_id, category_id, count = order_['product_id'], order_['category_id'], order_['quantity']
        deliver = delivery_products.delivery_lot(user_id, category_id, product_id, count)
        if not deliver:
            log(f'Не удалось выдать заказ {order_id}. Данные заказа - product_id: {product_id}, category_id: {category_id}'
                f'count: {count}', lvl=4)
            return False
        bot.edit_message_reply_markup(user_id, message_id=msg_id, reply_markup=K().add(B('✅ Заказ выполнен', None, 'decorate')))
        log(f'Пользователь {user_id} оплатил заказ {order_id}', lvl=3)
        JSON_Orders.update_order_status(user_id, order_id, True)
        referal = db.get_user_column(user_id, 'from_referal')
        if referal:
            procent = int(order_['amount']) * (cfg.GIFT_PROCENT_REFERAL / 100)
            db.add_money_user(referal, procent)
            log(f'Пользователь {referal} получил {procent} рублей за оплату заказа {order_id}', lvl=3)
            bot.send_message(referal, f'*🥳 Пользователь - 6034429696 пополнил баланс! На ваш счет зачислено* `{procent}` рублей!', parse_mode='Markdown')
        else:
            log(referal)
        buys = db.get_user_column(user_id, 'buys')
        db.update_user_column(user_id, 'buys', buys + 1)
        return True

    def check_status_payment(self, order_id):
        """

        Функция проверки статуса платежа (не существует)
        (Здесь автоматически возвращает True)


        :param order_id:
        :return:
        """
        return True
