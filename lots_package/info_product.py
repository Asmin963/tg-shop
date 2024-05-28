import time

from tools.logger import log
from config import cfg
import os
import json
import random
from typing import Optional, List
import shutil


class ProductsInfo:
    """
    Класс для работы с json файлами товаров
    [
        {
            "id": id,
            "name": "",
            "image": "",
            "description": "",
            "products": [{
                "id": id,
                "name": "",
                "description": "",
                "count": int,
                "price": int,
                "image": "",
            }]
        }
    ]
    """
    def __init__(self):
        if not os.path.exists(cfg.PRODUCTS_INFO_PATH):
            with open(cfg.PRODUCTS_INFO_PATH, "w", encoding='utf-8') as f:
                json.dump([], f)
        with open(cfg.PRODUCTS_INFO_PATH, "r", encoding='utf-8') as f:
            data = f.read()
            if not data:
                self.products = []
            else:
                self.products = json.loads(data)

    def read_all_products(self):
        with open(cfg.PRODUCTS_INFO_PATH, "r", encoding='utf-8') as f:
            data = f.read()
            if not data:
                self.products = []
            else:
                self.products = json.loads(data)

    def get_products(self, category_id: int, argument=None) -> list:
        """
        Получает все товары из категории
        :param category_id: идентификатор категории
        :param argument: аргумент по которому будет производиться поиск
        :return: список товаров
        """
        try:
            if not argument:
                return next((cat["products"] for cat in self.products if cat["id"] == category_id), [])
            else:
                return list(map(str, [prod[argument] for prod in next((cat["products"] for cat in self.products if cat["id"] == category_id), [])]))
        except Exception as e:
            log(f"Ошибка при получении товаров из категории - {e}")
            return []

    def get_product(self, category_id, argument=None, value=None) -> dict:
        try:
            products = next((cat["products"] for cat in self.products if cat["id"] == str(category_id)), [])
            if argument and value:
                return next((prod for prod in products if prod[argument] == str(value)), {})
            else:
                return products
        except Exception as e:
            log(f"Ошибка при получении товаров из категории - {e}", lvl=2)
            return {}

    def get_category(self, category_id: str) -> dict:
        """
        Получает категорию
        :param category_id: идентификатор категории
        :return: категория
        """
        try:
            return next((cat for cat in self.products if cat["id"] == category_id), {})
        except Exception as e:
            log(f"Ошибка при получении категории - {e}")
            return {}

    def add_category(self, name: str, description: str, image: Optional[str] = None, id: Optional[str] = None) -> bool:
        """
        Добавляет категорию
        :param name: название
        :param description: описание
        :param image: Изображение
        :param id: Номер (если отсутствует, то генерируется случайный)
        :return:
        """
        try:
            if not id:
                while True:
                    idetifity = ''.join(str(random.randint(0, 9)) for _ in range(5))
                    if not any(cat["id"] == idetifity for cat in self.products):
                        break
            else:
                idetifity = id
            if any(cat["id"] == idetifity for cat in self.products):
                log(f"Категория с таким идентификатором уже существует")
                return False
            new_category = {
                "id": idetifity,
                "name": name,
                "image": image,
                "description": description,
                "products": []
            }
            self.products.append(new_category)
            with open(cfg.PRODUCTS_INFO_PATH, "w", encoding='utf-8') as f:
                json.dump(self.products, f, indent=4, ensure_ascii=False)
            log(f'Добавлена категория "{name}". "{description}"')
            return True
        except Exception as e:
            log(f"Ошибка при добавлении данных категории - {e}")
            return False

    def delete_product(self, category_id: str, product_id: str) -> bool:
        """
        Удаляет товар из указанной категории.
        :param category_id: ID категории, из которой нужно удалить товар.
        :param product_id: ID товара, который нужно удалить.
        :return: True, если товар успешно удален, False в противном случае.
        """
        try:
            category_index = next((index for index, cat in enumerate(self.products) if cat["id"] == category_id), None)
            if category_index is None:
                log(f'Категории с ID {category_id} не существует', lvl=2)
                return False

            product_index = next((index for index, prod in enumerate(self.products[category_index]["products"]) if
                                  prod["id"] == product_id), None)
            if product_index is None:
                log(f'Товара с ID {product_id} в категории {category_id} не существует', lvl=2)
                return False

            del self.products[category_index]["products"][product_index]

            with open(cfg.PRODUCTS_INFO_PATH, "w", encoding='utf-8') as f:
                json.dump(self.products, f, indent=4, ensure_ascii=False)

            log(f'Товар с ID {product_id} успешно удален из категории {category_id}')
            return True
        except Exception as e:
            log(f"Ошибка при удалении товара - {e}", lvl=3)
            return False

    def add_product(self, category_id: str, name: str, description: str, price: int,
                    count=0,  image: Optional[str] = None, product_id: int = None):
        """
        Добавляет товар с уже существующую категорию

        :param category_id: ID категории
        :param product_id: ID товара
        :param name: Название
        :param description: Описание
        :param price: Цена
        :param count: Кол-во
        :param image: Изображение (Optional)
        :return: True, если товар добавлен; False, если категория {category_id} не была создана ранее или товар с таким идентификатором уже существует
        """

        if not product_id:
            while True:
                idetifity = ''.join(str(random.randint(0, 9)) for _ in range(5))
                if not any(p['id'] == product_id for p in [cat for cat in self.products]):
                    product_id = idetifity
                    break

        if not any(str(cat["id"]) == str(category_id) for cat in self.products):
            log(f'Категории {category_id} не существует', lvl=2)
            return False

        if any(prod == product_id for prod in self.get_products(category_id, "id")):
            log(f'Товар с таким идентификатором уже существует', lvl=2)
            return False

        try:
            new_product = {
                "id": product_id,
                "name": name,
                "description": description,
                "price": price,
                "count": count,
                "image": image
            }
            for cat in self.products:
                if int(cat["id"]) == int(category_id):
                    cat["products"].append(new_product)
                    break

            with open(cfg.PRODUCTS_INFO_PATH, "w", encoding='utf-8') as f:
                json.dump(self.products, f, indent=4, ensure_ascii=False)

            log(f'Добавил новый продукт с идентификатором {product_id}')
            return new_product
        except Exception as e:
            log(f"Ошибка при добавлении данных товара - {e}", lvl=3)
            return False

    def get_categories(self, argument=None) -> list:
        """
        Возвращает список категорий
        """
        with open(cfg.PRODUCTS_INFO_PATH, "r", encoding='utf-8') as f:
            data = f.read()
            if not data:
                self.products = []
            else:
                self.products = json.loads(data)
        try:
            if not argument:
                return self.products
            else:
                return [cat[argument] for cat in self.products]
        except Exception as e:
            log(f"Ошибка при получении категорий - {e}", lvl=3)
            return []

    def get_products_absolute(self, ids: list) -> list:
        """
        Получает список товаров во всех категориях
        :param ids: список идентификаторов товаров
        """
        try:
            categories = self.get_categories()
            for category in categories:
                for product in category["products"]:
                    if str(product["id"]) in ids:
                        yield product
        except Exception as e:
            log(f"Ошибка при получении товаров - {e}", lvl=3)
            return []

    def del_category(self, category: str) -> bool:
        """
        Метод для удаления категории

        :param category: ID категории
        :return:
        """
        try:
            if os.path.exists(os.path.join(cfg.CATEGORY_PATH, str(category))):
                shutil.rmtree(os.path.join(cfg.CATEGORY_PATH, str(category)))
            for cat in self.products:
                if cat['id'] == str(category):
                    self.products.remove(cat)
                    with open(cfg.PRODUCTS_INFO_PATH, "w", encoding='utf-8') as f:
                        json.dump(self.products, f, indent=4, ensure_ascii=False)
                    log(f'Категория {category} успешно удалена')
                    return True
            log(f'Категория не была удалена')
            return False
        except Exception as e:
            log(f"Ошибка при удалении категории - {e}", lvl=3)
            return False

    def edit_product_data(self, category: str, product: str, argument: str, value: str | int) -> bool:
        """
        :param category: ID категории
        :param product: ID Товара
        :param argument: ключ, который будем изменять. Пример: (count, image, price)
        :param value: Значение, на которое меняем
        :return:
        """
        try:
            cat = next((p for p in self.products if p['id'] == category), {})
            if not cat:
                log(f'Категории {category} не существует', lvl=2)
                return False
            prod = next((p for p in cat['products'] if p['id'] == product), {})
            prod[argument] = value
            with open(cfg.PRODUCTS_INFO_PATH, "w", encoding='utf-8') as f:
                json.dump(self.products, f, indent=4, ensure_ascii=False)
            return True
        except KeyError as e:
            log(f"KeyError - {e}", lvl=3)
            raise e
        except Exception as e:
            log(f"Ошибка при изменении данных товара - {e}", lvl=3)
            return False


class CategoryInfo:
    """
    {
        "id": Уникальный номер категории,
        "name": Название категории,
        "image": Изображение,
        "description": Описание категории,
        "products": Список товаров
    }
    """
    def __init__(self, data):
        self.data = data

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")


class ProductInfo:
    """
            {
                "id": Уникальный номер товара,
                "name": Название товара,
                "description": Описание товара,
                "price": Цена (в рублях),
                "count": Кол-во товара,
                "image": Изображение
            }
    """
    def __init__(self, data):
        self.data = data

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")
