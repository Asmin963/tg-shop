from bot import bot
from tools.logger import log
from telebot import types
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B, ReplyKeyboardMarkup as RK, KeyboardButton as KB
from config import cfg
import lots_package
from Bot.Shop import keyboards


@bot.message_handler(commands=['add_lot'])
def add_lot_handler(m: types.Message):
    if m.chat.id not in cfg.ADMINS:
        log(f'{m.chat.id} пытался добавить товар')
        return
    cats = lots_package.products_json.get_categories()
    M = K(row_width=2)
    M.add(*[B(p['name'], None, f'func=add_lot_to_cat-cat={p["id"]}-from=add_lot_handler') for p in cats]).add(
        B("➕ Создать новую категорию", None,
          'from=add_lot_handler-func=new_category'))
    bot.send_message(m.chat.id, '*Выберите категорию:*', parse_mode='Markdown', reply_markup=M)

    """

    Набор функций для создания категории

    """


def new_category(call):
    M = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('❌ Отменить'))
    bot.register_next_step_handler(
        (bot_msg := bot.send_message(call.message.chat.id, '✏️ *Введите название новой категории:*',
                                     parse_mode='Markdown',
                                     reply_markup=M)), name_new_category, bot_msg)


def name_new_category(m, bot_msg):
    bot.delete_message(m.chat.id, m.message_id)
    bot.delete_message(m.chat.id, bot_msg.message_id)
    if m.content_type != 'text':
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Название категории не может быть пустым*', parse_mode='Markdown')),
            name_new_category, bot_msg)
        return
    name_category = m.text.strip()
    if m.text == '❌ Отменить':
        bot.send_message(m.chat.id, "❌ *Отменено*", reply_markup=keyboards.main_keyboard, parse_mode="Markdown")
        return
    if not name_category:
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Название категории не может быть пустым*', parse_mode='Markdown')),
            new_category, bot_msg)
        return
    if name_category in lots_package.products_json.get_categories(argument="name"):
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Категория с таким названием уже существует*', parse_mode='Markdown')),
            new_category, bot_msg)
        return
    bot.register_next_step_handler(
        (bot_msg := bot.send_message(m.chat.id, '✏️ *Введите описание новой категории:*', parse_mode='Markdown')),
        desc_new_category,
        name_category, bot_msg)


def desc_new_category(m, name_category, bot_msg):
    if m.content_type != 'text':
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Описание категории не может быть пустым*', parse_mode='Markdown')),
            new_category, bot_msg)
        return
    desc_category = m.text.strip()
    bot.delete_message(m.chat.id, bot_msg.message_id)
    bot.delete_message(m.chat.id, m.message_id)
    if m.text == '❌ Отменить':
        bot.send_message(m.chat.id, "❌ *Отменено*", reply_markup=keyboards.main_keyboard, parse_mode="Markdown")
        return
    if not desc_category:
        bot.register_next_step_handler((bot_msg := bot.send_message(
            m.chat.id, '*❌ Описание категории не может быть пустым*', parse_mode='Markdown')), desc_new_category,
                                       name_category, bot_msg)
        return
    if name_category in lots_package.products_json.get_categories(argument="description"):
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Категория с таким описанием уже существует*',
                                         parse_mode='Markdown')), desc_new_category, name_category, bot_msg)
        return
    M = types.ReplyKeyboardMarkup(resize_keyboard=True)
    M.add(types.KeyboardButton('Без изображения'), types.KeyboardButton('❌ Отменить'))
    bot.register_next_step_handler(
        (bot_msg := bot.send_message(m.chat.id, "🖼 *Отправьте изображение для новой категории:*", parse_mode="Markdown",
                                     reply_markup=M)),
        image_new_category, name_category, desc_category, bot_msg)


def image_new_category(m, name_category, desc_category, bot_msg):
    bot.delete_message(m.chat.id, bot_msg.message_id)
    if m.content_type == 'text' and m.text == 'Без изображения':
        bot.delete_message(m.chat.id, m.message_id)
        lots_package.products_json.add_category(name_category, desc_category)
        bot.send_message(m.chat.id, '✅ *Категория успешно создана*', parse_mode='Markdown',
                         reply_markup=keyboards.main_keyboard)
        return
    if m.text == '❌ Отменить':
        bot.send_message(m.chat.id, "❌ *Отменено*", reply_markup=keyboards.main_keyboard, parse_mode="Markdown")
        return
    if m.content_type != 'photo':
        bot.delete_message(m.chat.id, m.message_id)
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Отправьте изображение в формате jpg/png*',
                                         parse_mode="Markdown", reply_markup=RK(resize_keyboard=True).row(KB('❌ Отменить'), KB('Без изображения')))),
            image_new_category, name_category, desc_category, bot_msg)
        return
    image = m.photo[0].file_id
    bot.delete_message(m.chat.id, m.message_id)
    lots_package.products_json.add_category(name_category, desc_category, image=image)
    bot.send_message(m.chat.id, '✅ *Категория успешно создана*', parse_mode='Markdown',
                     reply_markup=keyboards.main_keyboard)


    """
    
    Набор функций для добавление товара в уже созданную категорию
    
    """


def add_lot_to_cat(call, category_id: int):
    M = types.ReplyKeyboardMarkup(resize_keyboard=True)
    M.add(types.KeyboardButton('❌ Отменить'))
    bot.register_next_step_handler(
        (bot_msg := bot.send_message(call.message.chat.id, '✏️ *Введите название товара:*', parse_mode='Markdown',
                                     reply_markup=M)), name_new_product, category_id, bot_msg)


def name_new_product(m: types.Message, category_id: int, bot_msg):
    bot.delete_message(m.chat.id, bot_msg.message_id)
    bot.delete_message(m.chat.id, m.message_id)
    if m.content_type != 'text':
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Название товара не может быть пустым*', parse_mode='Markdown')),
            name_new_product, bot_msg)
        return
    name_product = m.text.strip()
    if m.text == '❌ Отменить':
        bot.send_message(m.chat.id, "❌ *Отменено*", reply_markup=keyboards.main_keyboard, parse_mode="Markdown")
        return
    if not name_product:
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Название товара не может быть пустым*', parse_mode='Markdown')),
            name_new_product, category_id, bot_msg)
        return
    if name_product in lots_package.products_json.get_products(category_id, argument="name"):
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Товар с таким названием уже существует*',
                                         parse_mode='Markdown')),
            name_new_product, category_id, bot_msg)
        return
    bot.register_next_step_handler(
        (bot_msg := bot.send_message(m.chat.id, '✏️ *Введите описание нового товара:*', parse_mode='Markdown',
                                     reply_markup=keyboards.cancel_keyboard)),
        desc_new_product,
        category_id, name_product, bot_msg)


def desc_new_product(m: types.Message, category_id: int, name_product: str, bot_msg):
    bot.delete_message(m.chat.id, bot_msg.message_id)
    bot.delete_message(m.chat.id, m.message_id)
    if m.content_type != 'text':
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Описание товара не может быть пустым*', parse_mode='Markdown')),
            desc_new_product, bot_msg)
        return
    desc_product = m.text.strip()
    if m.text == '❌ Отменить':
        bot.send_message(m.chat.id, "❌ *Отменено*", reply_markup=keyboards.main_keyboard, parse_mode="Markdown")
        return
    if not desc_product:
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Описание товара не может быть пустым*', parse_mode='Markdown')),
            desc_new_product, category_id,
            name_product, bot_msg)
        return
    if name_product in lots_package.products_json.get_products(category_id, argument="description"):
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Товар с таким описанием уже существует*',
                                         parse_mode='Markdown', reply_markup=RK(resize_keyboard=True).row(KB('❌ Отменить'), KB('Без изображения')))),
            desc_new_product, category_id, name_product, bot_msg)
        return
    M = types.ReplyKeyboardMarkup(resize_keyboard=True)
    M.add(types.KeyboardButton('Без изображения'), types.KeyboardButton('❌ Отменить'))
    bot.register_next_step_handler(
        (bot_msg := bot.send_message(m.chat.id, "🖼 *Отправьте изображение для нового товара*", parse_mode="Markdown",
                                     reply_markup=M)),
        image_new_product, category_id, name_product, desc_product, bot_msg)


def image_new_product(m, category_id, name, desc, bot_msg):
    bot.delete_message(m.chat.id, bot_msg.message_id)
    bot.delete_message(m.chat.id, m.message_id)
    M = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('❌ Отменить'))
    if m.content_type == 'text':
        if m.text == 'Без изображения':
            bot.register_next_step_handler(
                (bot_msg := bot.send_message(m.chat.id, f'💶 *Введите цену на товар:*', parse_mode='Markdown',
                                             reply_markup=M)),
                price_new_product,
                category_id, name, desc, bot_msg)
            return
        if m.text == '❌ Отменить':
            bot.send_message(m.chat.id, "❌ *Отменено*", reply_markup=keyboards.main_keyboard,
                             parse_mode="Markdown")
            return
    if m.content_type != 'photo':
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Отправьте изображение в формате jpg/png*',
                                         parse_mode="Markdown", reply_markup=RK(resize_keyboard=True).row(KB('❌ Отменить'), KB('Без изображения')))),
            image_new_product, category_id, name, desc, bot_msg)
        return
    image = m.photo[0].file_id
    M = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('❌ Отменить'))
    bot.register_next_step_handler(
        (bot_msg := bot.send_message(m.chat.id, f'💶 *Введите цену на товар:*', parse_mode='Markdown', reply_markup=M)),
        price_new_product,
        category_id, name, desc, bot_msg, image=image)


def price_new_product(m, category_id, name, desc, bot_msg, image=None):
    bot.delete_message(m.chat.id, bot_msg.message_id)
    bot.delete_message(m.chat.id, m.message_id)
    if m.content_type != 'text':
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Цена не может быть пустой*', parse_mode='Markdown')),
            price_new_product,
            category_id, name, desc, bot_msg, image=image)
        return
    price = m.text
    try:
        if float(price) < 0:
            bot.register_next_step_handler(
                (bot_msg := bot.send_message(m.chat.id, '*❌ Цена не может быть отрицательной*', parse_mode='Markdown')),
                price_new_product,
                category_id, name, desc, bot_msg, image=image)
            return
    except Exception as e:
        log(str(e), lvl=2)
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Цена должна быть числом*', parse_mode='Markdown')),
            price_new_product,
            category_id, name, desc, bot_msg, image=image)
        return

    if not m.text:
        bot.register_next_step_handler(
            (bot_msg := bot.send_message(m.chat.id, '*❌ Цена не может быть пустой*', parse_mode='Markdown')),
            price_new_product,
            category_id, name, desc, bot_msg, image=image)
        return
    price = float(price)
    add_prod = lots_package.products_json.add_product(category_id, name, desc, price, image=image)
    if not add_prod:
        bot.send_message(m.chat.id, f'*❌ Не удалось добавить товар*', parse_mode='Markdown',
                         reply_markup=keyboards.main_keyboard)
        return
    bot.send_message(m.chat.id, f'✅ *Товар успешно добавлен*', parse_mode='Markdown',
                     reply_markup=keyboards.main_keyboard)
