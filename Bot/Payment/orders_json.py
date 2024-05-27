import json
import os
from tools.logger import log
import random
import string


class OrderManagerJSON:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                json.dump({}, file, indent=4)
        try:
            ords = self.load_orders()
        except Exception as e:
            self.save_orders({})
            log(f'Файл с заказами не найден. Создан пустой файл.')

    def load_orders(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
        return data

    def save_orders(self, data):
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def add_order_to_json(self, user_id, order, order_id):
        orders = self.load_orders()
        if user_id not in list(orders.keys()):
            orders[user_id] = {}
        orders[user_id][order_id] = order
        with open(self.file_path, 'w') as file:
            json.dump(orders, file, indent=4)

    def generate_order_id(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    def add_order(self, user_id: str, category_id: str, product_id: str,
                  name: str, price: int, quantity: int, time: str, amount: int, lang='ru',
                  currency="RUB", desc='Payment', status=False):
        try:
            order_id = self.generate_order_id()
            new_order = {
                'category_id': category_id,
                'product_id': product_id,
                'name': name,
                'price': price,
                'quantity': quantity,
                'time': time,
                'amount': amount,
                'order_status': status,
                'order_id': order_id,
                'lang': lang,
                "currency": currency,
                "desc": desc
            }
            self.add_order_to_json(str(user_id), new_order, order_id)
            log(f'Сохранил новый заказ в файл JSON')
            return OrderInfo(new_order)
        except Exception as e:
            log(f'Ошибка при добавлении заказа: {e}')
            return False

    def get_orders_by_user_id(self, user_id, order_id=None):
        orders = self.load_orders()
        if not order_id:
            return orders.get(user_id, {})
        else:
            try:
                return orders[str(user_id)][str(order_id)]
            except KeyError:
                return {}

    def update_order_status(self, user_id, order_id, new_status):
        orders = self.load_orders()
        if user_id in list(orders.keys()) and order_id in list(orders[user_id].keys()):
            orders[user_id][order_id]['order_status'] = new_status
            self.save_orders(orders)
            log(f'Обновил статус заказа {order_id}: {new_status}')
            return True
        return False

    def update_order_details(self, user_id, order_id, new_details):
        orders = self.load_orders()
        if user_id in list(orders.keys()) and order_id in list(orders[user_id].keys()):
            orders[user_id][order_id].update(new_details)
            self.save_orders(orders)
            log(f'Обновил детали заказа {order_id}: {new_details}')
            return True
        return False

    def delete_order_(self, user_id: str, order_id: str):
        orders = self.load_orders()
        if user_id in list(orders.keys()) and order_id in list(orders[user_id].keys()):
            del orders[user_id][order_id]
            self.save_orders(orders)
            log(f'Удалил заказ {order_id} пользователя {user_id}')
            return True
        return False

    def _status(self, user_id, order_id):
        """
        Проверяет статус заказа
        :param user_id:
        :param order_id:
        :return:
        """
        orders = self.load_orders()
        if user_id in list(orders.keys()) and order_id in list(orders[user_id].keys()):
            return orders[user_id][order_id]['order_status']
        return False

    def _last_orders(self, user_id, count):
        try:
            orders = self.load_orders()
            if user_id in list(orders.keys()):
                return list(orders[user_id].values())[-count:]
            else:
                return []
        except Exception as e:
            log(f"Ошибка при получении последних заказов - {e}", lvl=4)
            return False


class OrderInfo:
    def __init__(self, data):
        self.category_id = data['category_id']
        self.product_id = data['product_id']
        self.name = data['name']
        self.price = data['price']
        self.quantity = data['quantity']
        self.time = data['time']
        self.amount = data['amount']
        self.order_status = data['order_status']
        self.order_id = data['order_id']
        self.lang = data['lang']
        self.currency = data['currency']
        self.desc = data['desc']



