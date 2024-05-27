from telebot import types
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
from lots_package import products_json, favorite_products
from config import cfg
from tools.logger import log
from Bot.Payment import aaio


main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    types.KeyboardButton(text='📖 Все категории'),
    types.KeyboardButton(text='📄 Наличие товаров'),
    types.KeyboardButton(text='👤 Профиль'),
    types.KeyboardButton(text='🆘 Помощь'),
    types.KeyboardButton(text='💎 О магазине')
)

profile_keyboard = types.InlineKeyboardMarkup(row_width=2).add(
    types.InlineKeyboardButton(text='💸 История заказов', callback_data='func=history_orders-count=10'),
    types.InlineKeyboardButton(text='🎁 Активировать купон', callback_data='func=activate_coupon-from=profile'),
    types.InlineKeyboardButton(text='🤝 Реферальная система', callback_data='func=referal_system-from=profile'),
    types.InlineKeyboardButton(text='⭐️ Избранные товары', callback_data='func=menu_favorite_products-from=profile'),
    types.InlineKeyboardButton(text='💳️ Пополнить баланс', callback_data='func=refill-from=profile')
)

help_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text='📩 Написать', url=f'https://t.me/arthells')
)

cancel_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
    types.KeyboardButton(text='❌ Отменить')
)


def categories_all(for_user=False):
    categories = [p for p in products_json.get_categories() if p['products']] if for_user else products_json.get_categories()
    categories_keyboard = types.InlineKeyboardMarkup(row_width=2).add(
        *[types.InlineKeyboardButton(text=category['name'],
                                     callback_data=f'func=open_category-category={category["id"]}') for category
          in
          categories]
    )
    if not categories:
        return False
    else:
        return categories_keyboard


def category_keyboard(category_id, user_id=None):
    """
    Генерирует клавиатуру товаров в категории
    :param category_id:
    :return:
    """
    products = products_json.get_products(category_id)
    if user_id and user_id not in cfg.ADMINS:
        products = [p for p in products if p['count'] > 0]
    products_keyboard = (K(row_width=1).add(
        *[B(text=f'{product["name"]} | {product["price"]} ₽ | {product["count"]} шт.',
            callback_data=f'func=open_product-cat={category_id}-prod={product["id"]}') for product in products]).
                         add(B(text='Назад ко всем категориям', callback_data='func=categories_menu-from=category_menu')))
    if user_id and user_id in cfg.ADMINS:
        products_keyboard.add(
            B('❌ Удалить категорию', None, f'func=delete_category-cat={category_id}-from=category_menu'))
    return products_keyboard


def product_keyboard(user_id, product_id, category_id, for_only_user=False):
    M = K(row_width=5).add(
        *[B(text=i, callback_data=f'func=buy-cat={category_id}-prod={product_id}-count={i}') for i in range(1, 11)]
    ).add(B(text='🔙 Назад', callback_data=f'func=open_category-cat={category_id}')).add(
        B(text='🔙 Назад ко всем категориям',
          callback_data='func=categories_menu-from=product_menu')
    )
    if favorite_products.is_favorite(user_id, product_id):
        M.add(B('🗑 Удалить из избранного', None, f'func=delete_favorite-cat={category_id}-prod={product_id}'))
        log('Лот уже есть в изобранном')
    else:
        M.add(B('⭐️ Добавить в избранное', None, f'func=add_favorite-cat={category_id}-prod={product_id}'))
        log('Лота нет в изобранном')
    if user_id in cfg.ADMINS and not for_only_user:
        M.row(B('❌ Удалить лот', None,
                f'func=delete_prod-cat={category_id}-prod={product_id}-from=prod_menu'),
              B('📦 Загрузить товары', None,
                f'func=upload_products-cat={category_id}-prod={product_id}-from=prod_menu'))
        M.row(B('⚙️ Изменить настройки', None, f'func=edit_product-cat={category_id}-prod={product_id}-from=prod_menu'),
              B('🔑 Выдать товар', None, f'func=send_product-cat={category_id}-prod={product_id}-from=prod_menu'))
    return M


admin_about_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text='✏️ Изменить текст', callback_data=f'admin-func=edit_about_text-from=about')
)

hide_keyboard = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text='🔙 Скрыть', callback_data='hide_keyboard')
)


def keyboard_favorite_products(user_id):
    M = K(row_width=1)
    favorites = favorite_products.get_favorite_products(user_id)
    M.add(*[B(f["name"], None, f'func=favorite_lot-cat={f["category"]}-prod={f["id"]}-from=favorite_menu') for f in favorites])
    M.row(B('🔙 Скрыть', None, 'hide_keyboard'))
    return M


def keyboard_favorite_product(category_id, product_id):
    M = K(row_width=1)
    M = K(row_width=5).add(
        *[B(text=i, callback_data=f'func=buy-cat={category_id}-prod={product_id}-count={i}') for i in range(1, 11)]
    ).add(B(text='Назад', callback_data=f'func=open_category-cat={category_id}-from=favorite_menu')).add(
        B(text='Назад ко всем категориям',
          callback_data='func=categories_menu-from=favorite_menu')
    )
    M.row(B('🗑 Удалить из избранного', None, f'func=delete_favorite-cat={category_id}-prod={product_id}-from=favorite_menu'))

    return M


def order_keyboard(order_id, amount, lang, currency, desc):
    url = aaio.generate_payment_link(order_id, amount, currency, desc, lang)
    M = K(row_width=1).add(
        B(text='🚀 Перейти к оплате', url=url),
        B(text='✅ Проверить оплату', callback_data=f'func=check_status_order-order={order_id}'),
        B(text='❌ Отменить заказ', callback_data=f'func=cancel_order-order={order_id}')
    )
    return M