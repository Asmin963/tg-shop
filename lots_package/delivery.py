import json
from time import strftime

import lots_package
from tools.logger import log
from config import cfg
import os
from .info_product import ProductsInfo
from bot import bot
from database import dbase as db


Pi = ProductsInfo()


class Delivery:
    def __init__(self):
        pass

    def get_delivery_products(self, category_id: int, product_id: int, count: int):
        """
        Получает {count} товаров {product_id} Из категории {category_id}

        :param category_id:
        :param product_id:
        :param count:
        :return:
        """
        try:
            category_path = os.path.join(cfg.CATEGORY_PATH, f'{category_id}')
            if not os.path.exists(category_path):
                log(f'Категория {category_id} не найдена в хранилище товаров')
                return False
            product_file = os.path.join(category_path, f'{product_id}.txt')
            if not os.path.exists(product_file):
                log(f'Товар {product_id} не найден в хранилище товаров')
                return False
            with open(product_file, "r+") as f:
                products = [p.strip() for p in f.readlines() if p]
                if len(products) < count:
                    log(f'Недостаточно товаров для доставки')
                    return False
                delivery_product = products[:count]
                products = products[count:]
            with open(product_file, "w", encoding='utf-8') as f:
                f.write("\n".join([p.strip() for p in products if p]))
            return delivery_product
        except Exception as e:
            log(f'Ошибка при доставке товаров: {e}', lvl=2)

    def add_products(self, category: int, product_id: int, products: list,
                     absolut_add=False, replace_product=False):
        """
        Добавляет товары в файл с категорией

        :param category: номер категории
        :param product_id: номер товара
        :param products: товары для добавления
        :param absolut_add: если True, то в случае отсутвия директоии с товаром она будет создана, если же False, в том же случае return False
        :param replace_product: если True, то товарный файл заменяется, иначе товары добавляются
        :return:
        """
        try:
            category_path = os.path.join(cfg.CATEGORY_PATH, f'{category}')
            if not os.path.exists(category_path):
                if not absolut_add:
                    log(f'Категория {category} не найдена в хранилище товаров', lvl=2)
                    return False
                else:
                    os.makedirs(category_path)
            product_file = os.path.join(category_path, f'{product_id}.txt')
            if not os.path.exists(product_file):
                if not absolut_add:
                    log(f'Товар {product_id} не найден в хранилище товаров', lvl=2)
                    return False
                else:
                    with open(product_file, "w+") as f:
                        f.write("\n".join(list(map(str, products))) + '\n')
                    log(f'Создан новый файл с товаром {product_id} в категории {category}')
                    return True
            if replace_product:
                with open(product_file, "w+") as f:
                    f.write("\n".join(list(map(str, products))) + '\n')
                log(f'Товар {product_id} в категории {category} заменен')
            else:
                with open(product_file, "a+") as f:
                    f.write("\n".join(list(map(str, products))) + '\n')
                log(f'Добавил товары в {product_id} в категории {category}')
            return True
        except Exception as e:
            log(f'Ошибка при добавлении товаров в хранилище: {e}', lvl=3)
            return False
        finally:
            count = self.products_left(category, product_id)
            edit = lots_package.products_json.edit_product_data(category, product_id, "count", count)
            if not edit:
                log(f'Ошибка при добавлении товаров в хранилище json', lvl=3)
                return False
            else:
                log(f'Добавил товары в json')
                return True


    def products_left(self, category, product_id):
        """
        Проверяет количество товаров в категории и товаре

        :param category:
        :param product_id:
        :return:
        """
        try:
            category_path = os.path.join(cfg.CATEGORY_PATH, f'{category}')
            if not os.path.exists(category_path):
                log(f'Категория {category} не найдена в хранилище товаров')
                return False
            product_file = os.path.join(category_path, f'{product_id}.txt')
            if not os.path.exists(product_file):
                log(f'Товар {product_id} не найден в хранилище товаров')
                return False
            with open(product_file, "r+") as f:
                products = list(map(str.strip, f.readlines()))
                return len(products)
        except Exception as e:
            log(f'Ошибка при проверке количества товаров: {e}', lvl=2)

    def delivery_lot(self, user_id, category_id, product_id, count=1):
        try:
            prods = self.get_delivery_products(category_id, product_id, count)
            if not prods:
                bot.send_message(user_id, f'*❌ Недостаточно товаров для доставки*', parse_mode="Markdown")
                log(f'Недостаточно товаров для доставки')
                return False
            file = delivery_files.send_delivery_file(prods, category_id, product_id, count)
            try:
                bot.send_document(user_id, open(file, 'rb'))
            except Exception as e:
                log(f'Ошибка при отправке файла с товарами - {e}', lvl=3)
                bot.send_message(user_id, f'*❌ Ошибка при отправке файла с товарами*', parse_mode="Markdown")
                return False
            count = self.products_left(category_id, product_id)
            edit = lots_package.products_json.edit_product_data(category_id, product_id, "count", count)
            if edit:
                log(f'Обновил кол-во товаров. Номер товара - {product_id}. Номер - категории - {category_id}')
            else:
                log(f"Ошибка при обновлении кол-ва товаров. Номер товара - {product_id}. Номер - категории - {category_id}",
                    lvl=3)
            log(f"Отправил файл с товарами юзеру - {user_id}. Номер товара - {product_id}. Номер - категории - {category_id}")
            return True
        except Exception as e:
            log(f'Ошибка при отправке файла с товарами - {e}', lvl=2)
            return False









class Files:
    def __init__(self):
        pass

    def send_delivery_file(self, products, category: int, product_id: int, count):
        try:
            filename = f"{strftime('%Y-%m-%d_%H.%M.%S')}_{category}_{product_id}_{count}.txt"
            directory = os.path.join(cfg.PRODUCT_PATH, "sells")
            if not os.path.exists(directory):
                os.makedirs(directory)
            temp_file = os.path.join(directory, filename)
            with open(temp_file, 'w') as f:
                f.write("\n".join(products))
            return temp_file
        except Exception as e:
            log(f'Ошибка при отправке файла с товарами - {e}', lvl=2)
            return False

    def create_category(self, category_id):
        try:
            if os.path.exists(os.path.join(cfg.CATEGORY_PATH, str(category_id))):
                log(f'Категория с ID - {category_id} уже есть', lvl=2)
                return False
            os.mkdir(os.path.join(cfg.CATEGORY_PATH, str(category_id)))
            return True
        except Exception as e:
            log(f'Ошибка при создании категории {category_id} - {e}', lvl=2)
            return False

    def create_product_file(self, category_id, product_id):
        try:
            path = os.path.join(cfg.CATEGORY_PATH, str(category_id), f'{str(product_id)}.txt')
            if os.path.exists(path):
                log(f'Товар с ID - {product_id} уже есть', lvl=2)
                return False
            os.makedirs(os.path.join(cfg.CATEGORY_PATH, str(category_id)))
            with open(path, 'w', encoding='utf8') as f:
                f.write('')
            return True
        except Exception as e:
            log(f'Ошибка при создании товара {product_id} - {e}', lvl=3)
            return False


class FavoriteProducts:
    def __init__(self):
        self.favorites_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'favorites.json')
        if not os.path.exists(self.favorites_path):
            with open(self.favorites_path, "w", encoding='utf-8') as f:
                json.dump({}, f)
        with open(self.favorites_path, "r", encoding='utf-8') as f:
            data = f.read()
            if not data:
                self.data = []
            else:
                self.data = json.loads(data)

    def read_data(self):
        with open(self.favorites_path, "r", encoding='utf-8') as f:
            data = f.read()
            if not data:
                self.data = {}
            else:
                self.data = json.loads(data)

    def get_favorite_products(self, user_id: int):
        """
        Получение списка товаров из избранного по ID

        :param user_id:
        :return:
        """
        try:
            user_id = str(user_id)
            try:
                log(f'Favorites {user_id} - {self.data[user_id]}')
                return self.data[user_id]
            except KeyError:
                self.data[user_id] = []
                return False
        except Exception as e:
            log(f"Ошибка при получении товаров из категории - {e}", lvl=4)
            return False

    def save_favorite_product(self, user_id, category, product_id):
        """
        Добавляет товар в избранное

        :param user_id: айди юзера
        :param category: номер категории
        :param product_id: номер товара
        :return:
        """
        try:
            user_id = str(user_id)
            try:
                if not self.data[user_id]:
                    self.data[user_id] = []
            except KeyError:
                self.data[user_id] = []
            if self.data:
                ids = [prod['id'] for prod in self.data[user_id]]
                if product_id in ids:
                    log(f'Товар {product_id} уже есть в избранном', lvl=2)
                    return f'❌ *Товар* `{product_id}` *уже есть в избранном*'
            log(f'{str(category), "id", str(product_id)}')
            product = Pi.get_product(str(category), "id", str(product_id))
            log(f'Данные на сохранение - {product}')
            self.data[user_id].append({
                'name': product['name'],
                'category': category,
                'id': product_id
            })
            with open(self.favorites_path, "w", encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=True, indent=4)
            log(f'Добавлен товар {product_id} в категории {category} в избранное')
            return True
        except Exception as e:
            log(f'Ошибка при добавлении товаров в избранное: {e}', lvl=4)
            return False

    def delete_favorite_product(self, user_id, category_id, product_id):
        """
        Удаляет товар из избранного

        :param user_id:
        :param category_id:
        :param product_id:
        :return:
        """
        try:
            user_id = str(user_id)
            if user_id not in self.data:
                return False

            products = self.data[user_id]
            index_to_remove = None
            for idx, prod in enumerate(products):
                if prod['id'] == product_id and prod['category'] == category_id:
                    index_to_remove = idx
                    break

            if index_to_remove is not None:
                del self.data[user_id][index_to_remove]
                with open(self.favorites_path, "w", encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=True, indent=4)
                log(f'Удален товар {product_id} из категории {category_id} из избранного')
                return True
            else:
                log(f'Товар {product_id} не найден в категории {category_id} из избранного', lvl=2)
                return f'❌ *Товар* `{product_id}` *не найден в избранном*'

        except Exception as e:
            log(f'Ошибка при удалении товара из избранного: {e}', lvl=4)
            return False

    def is_favorite(self, user_id, product_id):
        """
        Проверяет, находится ли товар в избранном

        :param user_id:
        :param product_id:
        :return:
        """
        try:
            user_id = str(user_id)
            try:
                if not self.data[user_id]:
                    self.data[user_id] = []
            except KeyError:
                self.data[user_id] = []
            if self.data:
                ids = [prod['id'] for prod in self.data[user_id]]
                if product_id in ids:
                    log(f'Товар {product_id} уже есть в избранном', lvl=2)
                    return True
            return False
        except Exception as e:
            log(f'Ошибка при проверке товаров избранного: {e}', lvl=4)
            return False

delivery_files = Files()
delivery_products = Delivery()
favorite_products = FavoriteProducts()
