import telebot.types
from bot import bot
from telebot.types import BotCommand
from config import cfg

private_commands = [
    BotCommand(
        command='start.bat',
        description='Запуск/Перезапуск 🚀'
    )
]

admin_commands = [
    BotCommand(
        command='start.bat',
        description='Запуск/Перезапуск 🚀'
    ),
    BotCommand(
        command='add_lot',
        description='Добавить товар'
    ),
    BotCommand(
        command='add_promo',
        description='Добавить промокод'
    ),
    BotCommand(
        command='delete_promo',
        description='Удалить промокод'
    ),
    BotCommand(
        command='get_promos',
        description='Все промокоды'
    )
]

for chat_id in cfg.ADMINS:
    bot.set_my_commands(admin_commands, scope=telebot.types.BotCommandScopeChat(chat_id=chat_id))

bot.set_my_commands(private_commands, scope=telebot.types.BotCommandScopeAllPrivateChats())

