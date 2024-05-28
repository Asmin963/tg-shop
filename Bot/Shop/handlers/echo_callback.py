import Bot.Shop.handlers.echo_functions
from bot import bot
from tools.logger import log
from config import cfg
from Bot.Shop.tools import argment_from_callback
from .users import profile
import time
from .admins import add_product

TIME_LIMIT = 0.5

last_request_times = {}


def check_message_limit(user_id: int) -> bool:
    current_time = time.time()

    if user_id in last_request_times:
        if current_time - last_request_times[user_id] < TIME_LIMIT:
            return False

    last_request_times[user_id] = current_time
    return True


@bot.callback_query_handler(func=lambda x: True)
def handler_echo_callback(call):
    user_id = call.message.chat.id
    if not check_message_limit(user_id):
        bot.answer_callback_query(call.id, f'⌛️ Не так быстро! Попробуй через пару секунд', show_alert=True)
        return
    if "admin" in call.data and user_id not in cfg.ADMINS:
        return
    data = argment_from_callback(call.data)
    if "hide_keyboard" in call.data:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        return
    if 'decorate' in call.data:
        return
    try:
        if 'from' in call.data:
            if data['from'] == 'add_lot_handler':
                if "from" in call.data and 'func' in call.data:
                    func_name = data['func']
                    func = getattr(add_product, func_name)
                    if 'cat=' in call.data:
                        func(call, data['cat'])
                    else:
                        func(call)
                    return
            if data['from'] == 'profile':
                func_name = data['func']
                func = getattr(profile, func_name)
                func(user_id)
                return
        log(f'Получены данные callback - {data}')
        func_name = data['func']
        func = getattr(Bot.Shop.echo_func, func_name)
        aaargs = [data[key] for key in data.keys() if key not in ['to', 'func']]
        func(call, *aaargs)
        return True
    except AttributeError as e:
        log(f'AttributeError - {e}', lvl=4)
        return False
    except Exception as e:
        log(f'callback - {call.data}')
        log(f'Ошибка при обработке callback - {e}', lvl=4)
        return False
