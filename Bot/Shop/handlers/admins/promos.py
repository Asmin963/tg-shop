from bot import bot
from tools.logger import log
from telebot import types
from config import cfg
from tools import Promo


class PromoPanelMessages:
    def __init__(self):
        self.admin = cfg.ADMINS[0]
        self.bot = bot
        self.register_handlers()

    def register_handlers(self):
        @self.bot.message_handler(commands=['add_promo'], func=lambda m: m.chat.id == self.admin)
        def add_promo_command_handler(message: types.Message):
            self.bot.send_message(message.chat.id,
                                  '🔑 *Введите промокод в формате:*\n\n`(промокод)` `(кол-во токенов)` `(кол-во использований)`',
                                  parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
            self.bot.register_next_step_handler(message, self.final_add_promo)

        @self.bot.message_handler(commands=['delete_promo'], func=lambda m: m.chat.id == self.admin)
        def add_promo_command_handler(message: types.Message):
            self.bot.send_message(message.chat.id,
                                  '🔑 *Введите промокод для удаления*',
                                  parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
            self.bot.register_next_step_handler(message, self.delete_promo)

        @self.bot.message_handler(commands=['get_promos'], func=lambda m: m.chat.id == self.admin)
        def add_promo_command_handler(m: types.Message):
            all_promos = [f'`{p}`' for p in Promo.get_promo_codes().keys()]
            if not all_promos:
                bot.send_message(m.chat.id, f'🤷‍♂️ *Нет активных промкодов*', parse_mode='Markdown')
                return
            bot.send_message(m.chat.id, f'🎁 *Список активных промокодов:*\n{", ".join(all_promos)}', parse_mode='Markdown')

    def final_add_promo(self, message: types.Message):
        try:
            ms = list(map(str.strip, message.text.split()))
            if len(ms) != 3:
                self.bot.send_message(message.chat.id, '❌ *Неправильный формат*', parse_mode='Markdown')
                return
            if not ms[1].lstrip('0').isdigit() or not ms[2].lstrip('0').isdigit():
                self.bot.send_message(message.chat.id, '❌ *Неправильный формат*', parse_mode='Markdown')
                return
            promo, tokens, max_use = ms[0], int(ms[1]), int(ms[2])
            result = Promo.add_promo_code(promo, tokens, max_use)
            if result:
                self.bot.send_message(message.chat.id, f'✅ *Промокод* `{promo}` *на* `{tokens}` *запросов и на* `{max_use}` *использований успешно добавлен*',
                                     parse_mode='Markdown')
            else:
                if promo in Promo.get_promo_codes():
                    self.bot.send_message(message.chat.id, '❌ *Промокод уже добавлен*', parse_mode='Markdown')
                    return
                self.bot.send_message(message.chat.id, '❌ *Ошибка при добавлении токена*', parse_mode='Markdown')
        except Exception as e:
            log(f'Ошибка при добавлении промокода - {e}', lvl=4)
            self.bot.send_message(message.chat.id, f'❌ *Ошибка при добавлении промокода:*\n`{e}`', parse_mode='Markdown')

    def delete_promo(self, m):
        try:
            if m.text.strip() not in Promo.get_promo_codes():
                bot.send_message(m.chat.id, f'❌ *Промокод не существует*', parse_mode='Markdown')
                return
            delete_promo = Promo.remove_promo_code(m.text)
            if not delete_promo:
                self.bot.send_message(m.chat.id, f'❌ *Ошибка при удалении промокода*',
                                          parse_mode='Markdown')
                return
            self.bot.send_message(m.chat.id, f'✅ *Промокод* `{m.text}` *успешно удалён*',
                                  parse_mode='Markdown')
        except Exception as e:
            log(f'Ошибка при удалении промокода - {e}', lvl=4)
            self.bot.send_message(m.chat.id, f'❌ *Ошибка при удалении промокода:*\n`{e}`',
                                  parse_mode='Markdown')


promo_panel = PromoPanelMessages()
