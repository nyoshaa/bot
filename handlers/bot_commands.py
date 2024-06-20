__all__ = [
    "commands_for_bot",
]

from aiogram import types

bot_commands = (
    ("start", "Запуск бота"),
    ("register", "Регистрация пользователя"),
    ("token", "Проверка токена API Яндекс Диска"),
    ("add", "Добавление папки в отслеживание"),
    ("delete", "Удалить папку из отслеживания"),
    ("help", "Справка по боту"),
    ("status", "Показать статус пользователя"),
)

commands_for_bot = []
for cmd in bot_commands:
    commands_for_bot.append(types.BotCommand(command=cmd[0], description=cmd[1]))
