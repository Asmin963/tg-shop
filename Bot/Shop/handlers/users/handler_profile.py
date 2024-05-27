from bot import bot
from tools.logger import log
from telebot import types
from database import dbase
from config import cfg
from Bot.Shop import keyboards
from tools import Promo
from lots_package import favorite_products


class Profile:
    def __init__(self):
        pass

    def referal_system(self, user_id):
        try:
            refs_user = dbase.get_user_column(user_id, 'count_referals')
            message = """
*🎁 За каждого реферала будете получать {}% со всех его покупок.*

🔄️ *Приглашено:* `{}`

🔗 _Ваша персональная ссылка:_ 
`https://t.me/{}?start.bat=ref={}`"""
            bot.send_message(user_id, message.format(cfg.GIFT_PROCENT_REFERAL, refs_user,
                                                     bot.get_me().username, user_id),
                             reply_markup=keyboards.hide_keyboard, parse_mode='Markdown')
        except Exception as e:
            log(f'Ошибка при получении информации о пользователе: {e}', lvl=4)

    def activate_coupon(self, user_id):
        bot.register_next_step_handler(bot.send_message(user_id, f"*🎁 Введите ваш промокод...*", parse_mode='Markdown'),
                                       self.check_coupon, user_id)

    def check_coupon(self, m, user_id):
        coupon = m.text.lower()
        user_id = m.from_user.id
        promocodes = Promo.get_promo_codes()
        bot.delete_message(user_id, m.message_id)
        if coupon not in promocodes:
            bot.send_message(user_id, f"*❌ Промокода нет или истёк*", parse_mode='Markdown')
            return False
        if Promo.check_promo_code_usage(coupon, user_id):
            bot.send_message(user_id, f"*❌ Вы уже использовали этот промокод*", parse_mode='Markdown')
            return False
        bonuses = Promo.check_bonuses(coupon)
        dbase.add_money_user(user_id, bonuses)
        bot.send_message(user_id, f"*🎁 На ваш счет зачислено* `{bonuses}` *рублей!*", parse_mode='Markdown')
        Promo.use_promo_code(m.text, user_id)

    def menu_favorite_products(self, user_id):
        try:
            favorites = favorite_products.get_favorite_products(user_id)
            if not favorites:
                bot.send_message(user_id, f"*❌ Вы пока ничего не добавили в избранное.*",
                                 parse_mode='Markdown', reply_markup=keyboards.hide_keyboard)
                return False

            favorite_products_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
                *[types.InlineKeyboardButton(text=product["name"],
                                             callback_data=f'func=favorite_lot-cat={product["category"]}-prod={product["id"]}-from=favorite_menu')
                  for product in
                  favorites]
            ).add(
                types.InlineKeyboardButton(text='🔙 Скрыть', callback_data='hide_keyboard')
            )
            bot.send_message(user_id, '*Избранные товары:*', parse_mode='Markdown',
                             reply_markup=favorite_products_keyboard)
        except Exception as e:
            log(f'Ошибка при получении списка избранных товаров: {e}', lvl=2)
            return False
