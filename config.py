import configparser
import os.path


class Cfg:
    def __init__(self):
        self.filename = os.path.join(os.path.dirname(__file__), ".cfg")
        self.config = configparser.ConfigParser()
        self.config.read(self.filename, encoding='utf-8')

        self.TOKEN = self.config.get('DEFAULT', 'TOKEN')
        self.ADMINS = self.config.get('DEFAULT', 'ADMINS').split(',')
        self.REQUIRED_SUBSCRIPTIONS = self.config.get('DEFAULT', 'REQUIRED_SUBSCRIPTIONS')
        self.NEW_USER_NOTIFICATIONS = self.config.get('DEFAULT', 'NEW_USER_NOTIFICATIONS')
        self.GIFT_PROCENT_REFERAL = int(self.config.get('DEFAULT', 'GIFT_PROCENT_REFERAL'))
        self.WATERMARK = self.config.get('DEFAULT', 'WATERMARK')

        self.SECRET_KEY = self.config.get('DEFAULT', "SECRET_AAIO")
        self.MERCHANT_ID = self.config.get('DEFAULT', 'MERCHANT_ID')

        self.LOG_PATH = os.path.join(os.path.dirname(__file__), 'logs')
        self.CATEGORY_PATH = os.path.join(os.path.dirname(__file__), 'products', 'categories')
        self.PRODUCT_PATH = os.path.join(os.path.dirname(__file__), 'products')
        self.PRODUCTS_INFO_PATH = os.path.join(self.PRODUCT_PATH, 'data.json')
        self.ORDERS_PATH = os.path.join(self.PRODUCT_PATH, 'orders.json')

        self.START_MESSAGE = open(os.path.join(os.path.dirname(__file__), 'data', 'messages\\start.txt'), 'r', encoding='utf-8').read()
        self.HELP_MESSAGE = open(os.path.join(os.path.dirname(__file__), 'data', 'messages\\help.txt'), 'r', encoding='utf-8').read()
        self.ABOUT_MESSAGE = open(os.path.join(os.path.dirname(__file__), 'data', 'messages\\about.txt'), 'r', encoding='utf-8').read()
        self.PROFILE_MESSAGE = open(os.path.join(os.path.dirname(__file__), 'data', 'messages\\profile.txt'), 'r', encoding='utf-8').read()
        self.ORDER_MESSAGE = open(os.path.join(os.path.dirname(__file__), 'data', 'messages\\order.txt'), 'r', encoding='utf-8').read()

    def set(self, name, value):
        if isinstance(value, list):
            value = ','.join(list(map(str, value)))
        self.config.set('DEFAULT', name, value)
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
        self.__init__()

    def create(self, name, value):
        if isinstance(value, list):
            value = ','.join(list(map(str, value)))
        self.config.set('DEFAULT', name, str(value))
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
        self.__init__()


cfg = Cfg()

