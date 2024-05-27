from bot import bot
from tools.logger import log
from database import dbase as db
from Bot.Shop import keyboards


class Refill:
    def __init__(self):
        pass

    def add_refill(self, user_id, amount):
        try:
            add = db.add_money_user(user_id, amount)
            if not add:
                bot.send_message(user_id, f'*❌ Ошибка при пополнении баланса*', reply_markup=keyboards.main_keyboard,
                                 parse_mode="Markdown")
                log(f'Ошибка при пополнении баланса пользователя {user_id}', lvl=4)
                return False

            # Место для функции обработки пополнения

            bot.send_message(user_id, f'*Вы успешно пополнили свой баланс на {amount} рублей*',
                             reply_markup=keyboards.main_keyboard, parse_mode="Markdown")
            log(f'Пользователь {user_id} пополнил свой баланс на {amount} рублей', lvl=3)
            return True
        except Exception as e:
            log(f'Ошибка при пополнении баланса пользователя {user_id}: {e}', lvl=4)
            return False

    def recall_refill(self, user_id, amount, notification=False):
        try:
            rec = db.add_money_user(user_id, -amount)
            if not rec:
                log(f'Ошибка при списании средств пользователя {user_id}', lvl=4)
                return False

            # Место для функции обработки списаний средств

            if notification:
                bot.send_message(user_id, f'*⛔️ С вашего счета списано * `{amount}` ₽',
                                 reply_markup=keyboards.main_keyboard, parse_mode="Markdown")
            log(f'Списали со счета {user_id} сумму {amount}')
            return True
        except Exception as e:
            log(f'Ошибка при списании средств пользователя {user_id}: {e}', lvl=4)
            return False
