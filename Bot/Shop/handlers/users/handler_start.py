from bot import bot
from telebot import types
from database import dbase
from config import cfg
from Bot.Shop import keyboards
from tools.logger import log


@bot.message_handler(commands=['start.bat'])
def start_handler(m: types.Message):
    reffer = ""
    users = dbase.get_users()
    if len(m.text.split()) > 1:
        start_argument = m.text.split()[1].strip()
        if "ref" in start_argument:
            reffer = start_argument.split("=")[-1]
            log(reffer)
    if m.from_user.id not in users:
        dbase.add_user(m.from_user.id, m.from_user.first_name, m.from_user.last_name, m.from_user.language_code, m.from_user.username,
                       from_referal=reffer)
        if cfg.NEW_USER_NOTIFICATIONS:
            for admin in cfg.ADMINS:
                user = f'`{m.from_user.id}`' if not m.from_user.username else f'@{m.from_user.username}'
                bot.send_message(admin, f'👋 *Новый пользователь бота* {user}', parse_mode='Markdown')
    bot.send_message(m.chat.id, cfg.START_MESSAGE if not cfg.WATERMARK else cfg.START_MESSAGE + f'\n\n_{cfg.WATERMARK}_',
                     parse_mode='Markdown', reply_markup=keyboards.main_keyboard)
    if reffer:
        add_ref = dbase.add_referal(m.from_user.id, reffer)
        if add_ref:
            log(f"{m.from_user.id} стал рефералом {reffer}'a")
            bot.send_message(reffer, f'🥳 *У вас новый реферал - *`{m.from_user.id}`\n'
                                     f'*Вы будете получать* `{cfg.GIFT_PROCENT_REFERAL}` *процентов с пополнений!*',
                             parse_mode='Markdown')
        dbase.update_user_column(m.from_user.id, 'from_referal', str(reffer))

