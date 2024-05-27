import time

from tools.logger import log
from lots_package import delivery_files, products_json, delivery_products
from bot import bot
import Bot
import utils
import tools


if __name__ == "__main__":
    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as e:
            log(f'Ошибка при работе бота - {e}', lvl=3)
            time.sleep(20)



