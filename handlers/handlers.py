__all__ = [
    "register_message_handler",
    "check_yadisk",
]


import logging
import yadisk
import datetime as dt
from aiogram import Router, F, Bot
from aiogram import types
from aiogram.filters.command import Command, CommandStart, CommandObject
from aiogram.utils.deep_linking import decode_payload
# руководство по бд - https://pythonru.com/biblioteki/crud-sqlalchemy-core
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from config import CHECK_YADISK_INTERVAL
from connections import YandexDisk
from aiogram.utils.deep_linking import create_start_link
from db import async_session_maker, User, Folder
from .keyboards import keyboard_teacher_or_student, generate_keyboard_select_path
from .callbacks import callback_teacher_button_pressed, callback_student_button_pressed, callback_add_folder, callback_delete_folder


# настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

help_str = """Привет! Я бот, который поможет вам управлять вашими файлами на Яндекс Диске.
Вот мои основные команды:
/start - начать работу
/status - информация о текущем пользователе
/register - получить токен для работы с Яндекс.Диском (только для преподавателей)
/token - просмотреть токен (только для преподавателей)
/add - добавить папку в отслеживание (только для преподавателей)
/delete - удалить папку из отслеживания (только для преподавателей)"""


async def help_command(message: types.Message):
    """справочная команда"""
    await message.reply(help_str)
    logging.info(f"user {message.from_user.id} asked for help")


async def status_command(message: types.Message):
    """Информация о пользователе (и токене)"""
    async with async_session_maker() as session:
        session: AsyncSession
        query = select(User).where(User.tg_id == message.from_user.id)
        result = await session.execute(query)
        current_user = result.scalar()
        if current_user:
            if current_user.teacher_id:
                # пользователь - студент
                teacher_query = select(User).where(User.id == current_user.teacher_id)
                result = await session.execute(teacher_query)
                teacher = result.scalar()
                await message.reply(f"Текущий статус: Студент.\nПреподаватель: @{teacher.tg_username}")
            else:
                # пользователь - преподаватель
                if current_user.yandex_api_token:
                    select_folders_query = select(Folder.folder_path).where(Folder.user_tg_id == current_user.tg_id)
                    result = await session.execute(select_folders_query)
                    folders_paths = result.scalars().all()
                    paths_s = '\n'.join(folders_paths)
                    if not folders_paths:
                        paths_s = 'Еще не добавлено ни одной папки'
                    await message.reply(f"Текущий статус: Преподаватель.\nСинхронизация с яндекс.диском настроена.\nЧтобы увидеть токен: /token\nПапки в отслеживании:\n" + paths_s)
                else:
                    await message.reply(f"Текущий статус: Преподаватель.\nСинхронизация с яндекс.диском не настроена. Настроить: /register\nЧтобы стать студентом перейдите по ссылке от преподавателя.")
        else:
            await message.reply("Привет! Я бот, который поможет вам управлять вашими файлами на Яндекс Диске.\nВижу, вы еще не зарегистрированы. Скорее напишите /start")
    logging.info(f"user {message.from_user.id} asked for status")


async def start_command(message: types.Message):
    """Стартовая команда - регистрация нового пользователя"""
    async with async_session_maker() as session:
        session: AsyncSession
        query = select(User).where(User.tg_id == message.from_user.id)
        query = await session.execute(query)
        user = query.scalar()
        if not user:
            new_user = {
                "tg_id": message.from_user.id,
                "tg_username": message.from_user.username,
            }
            stmt = insert(User).values(**new_user)
            await session.execute(stmt)
            await session.commit()
    await message.reply("Привет! Я бот, который поможет вам управлять вашими файлами на Яндекс Диске.\nКто вы?", reply_markup=keyboard_teacher_or_student)
    logging.info(f"user {message.from_user.id} started the bot")


# https://docs.aiogram.dev/en/latest/utils/deep_linking.html
async def start_with_deeplink_command(message: types.Message, command: CommandObject):
    """Стартовая команда с deeplink"""
    args = command.args
    # расшифровываем аргументы, переданные через deep link
    payload = decode_payload(args)
    teacher_id = int(payload)
    async with async_session_maker() as session:
        session: AsyncSession
        query = select(User).where(User.tg_id == message.from_user.id)
        result = await session.execute(query)

        if result.scalar():
            stmt = update(User).where(User.tg_id == message.from_user.id).values(teacher_id=teacher_id)
            await session.execute(stmt)
            await message.answer("Теперь вы будете получать уведомления об изменениях на яндекс диске вашего преподавателя.")
        else:
            new_user = {
                "id": message.from_user.id,
                "tg_id": message.from_user.id,
                "tg_username": message.from_user.username,
                "teacher_id": teacher_id
            }
            stmt = insert(User).values(**new_user)
            await session.execute(stmt)
            await message.answer("Вы успешно зарегистрированы!\nТеперь вы будете получать уведомления об изменениях на яндекс диске вашего преподавателя.")
        await session.commit()
    logging.info(f"user {message.from_user.id} started the bot with deeplink")


async def register_command(message: types.Message):
    """Получение токена пользователя"""
    yd = YandexDisk()
    url = yd.get_code_url()
    await message.reply(f"Перейдите по ссылке и введите код: {url}")
    logging.info(f"user {message.from_user.id} is registering")


async def token_command(message: types.Message):
    """Проверка токена API Яндекс Диска"""
    async with async_session_maker() as session:
        session: AsyncSession
        query = select(User).where(User.tg_id == message.from_user.id)
        result = await session.execute(query)
        current_user = result.scalar()
        if current_user.yandex_api_token:
            link = await create_start_link(message.bot, payload=str(current_user.id), encode=True)
            await message.reply(f"Ваш токен: <code>{current_user.yandex_api_token}</code>\nСсылка для приглашения студентов: {link}", parse_mode='HTML')
        else:
            await message.reply("Вы еще не получили токен.\nПолучить: /register")
    logging.info(f"user {message.from_user.id} asked for token")


async def add_command(message: types.Message):
    """Добавление папки в отслеживание"""
    async with async_session_maker() as session:
        session: AsyncSession
        query = select(User).where(User.tg_id == message.from_user.id)
        result = await session.execute(query)
        current_user = result.scalar()
        if not current_user.yandex_api_token:
            await message.reply("Для работы с Яндекс.Диском нужен токен.\nПолучить: /register")
        with yadisk.Client(token=current_user.yandex_api_token) as client:
            # ищем все папки на диске с помощью рекурсивной функции
            # https://skillbox.ru/media/code/kak-rabotaet-rekursiya-funktsii-obyasnyaem-na-primere-python/
            folders_paths = []
            def get_all_folders(path):
                for item in client.listdir(path):
                    # ищем вложенные папки
                    if item.is_dir():
                        folders_paths.append(item.path)
                        # ищем вложенные папки во вложенных папках :)
                        get_all_folders(item.path)
            get_all_folders("/")
        # создаем новую клавиатуру из всех доступных на диске папок
        keyboard = generate_keyboard_select_path(folders_paths, "add")
        await message.answer("Выберете папку, которую хотите отслеживать", reply_markup=keyboard)
    logging.info(f"user {message.from_user.id} is adding folder")


async def delete_command(message: types.Message):
    """Удаление папки из отслеживания"""
    async with async_session_maker() as session:
        session: AsyncSession
        stmt = select(Folder.folder_path).where(Folder.user_tg_id == message.from_user.id)
        result = await session.execute(stmt)
        # создаем новую клавиатуру из отслеживаемых папок
        keyboard = generate_keyboard_select_path(result.scalars().all(), "delete")
        await message.answer("Выберете папку, которую хотите удалить из отслеживания", reply_markup=keyboard)
    logging.info(f"user {message.from_user.id} is deleting folder")


async def code_message(message: types.Message):
    """Ввод кода"""   
    code = message.text
    yd = YandexDisk()
    token = yd.get_token_from_code(code)
    if token is not None:
        # с токеном все нормально
        async with async_session_maker() as session:
            session: AsyncSession
            # запишем полученный токен в бд
            update_data = {'yandex_api_token': token}
            update_stmt = update(User).where(User.tg_id == message.from_user.id).values(update_data)
            await session.execute(update_stmt)
            await session.commit()
            query = select(User).where(User.tg_id == message.from_user.id)
            result = await session.execute(query)
            current_user = result.scalar()
            link = await create_start_link(message.bot, payload=str(current_user.id), encode=True)
        await message.reply(f"Токен успешно получен.\nТеперь вы можете пригласить студентов по этой ссылке: {link}\nДля добавления новых папок в отслеживание: /add")
    else:
        # что то не так
        await message.reply("Что-то пошло не так, попробуйте еще раз: /register")
    logging.info(f"user {message.from_user.id} entered the code")


async def check_yadisk(bot: Bot):
    """
    Асинхронная функция для проверки на изменения во всех отслеживаемых папках Яндекс.Диска.
    Должна запускаться с интервалом, определенным в config.CHECK_YADISK_INTERVAL.
    """
    logging.info("starting yadisk check")
    async with async_session_maker() as session:
        session: AsyncSession
        # Определяем время последней проверки, вычитая интервал проверки из текущего времени
        last_check_time = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=CHECK_YADISK_INTERVAL)
        # Формируем запрос на выборку всех преподавателей из базы данных
        select_teachers_stmt = select(User).where(User.yandex_api_token != None)
        result = await session.execute(select_teachers_stmt)
        teachers = result.scalars().all()  # Получаем список всех преподавателей
        for teacher in teachers:
            # Формируем запрос на выборку путей папок, отслеживаемых преподавателем
            select_folders_query = select(Folder.folder_path).where(Folder.user_tg_id == teacher.tg_id)
            result = await session.execute(select_folders_query)
            folders_paths = result.scalars().all()  # Получаем список путей папок
            # Формируем запрос на выборку Telegram ID студентов, привязанных к преподавателю
            select_students_tgs_query = select(User.tg_id).where(User.teacher_id == teacher.id)
            result = await session.execute(select_students_tgs_query)
            students_tg_ids = result.scalars().all()  # Получаем список Telegram ID студентов
            # Проверяем изменения в каждой папке
            yd = YandexDisk(teacher.yandex_api_token)
            for path in folders_paths:
                # Проверяем наличие обновлений в папке
                if yd.check_for_recent_updates(path, last_check_time):
                    # Формируем сообщение для студентов
                    message_text = f"Файлы в папке {path} изменились. Посмотрите скорее!"
                    # Отправляем сообщение каждому студенту
                    for student_tg_id in students_tg_ids:
                        await bot.send_message(student_tg_id, message_text, parse_mode='HTML')

    logging.info("yadisk check finished")


def register_message_handler(router: Router):
    """Маршрутизация"""
    router.message.register(help_command, Command("help"))
    router.message.register(status_command, Command("status"))
    router.message.register(start_with_deeplink_command, CommandStart(deep_link=True))
    router.message.register(start_command, Command("start"))
    router.message.register(register_command, Command("register"))
    router.message.register(token_command, Command("token"))
    router.message.register(add_command, Command("add"))
    router.message.register(delete_command, Command("delete"))
    # https://docs.aiogram.dev/en/latest/dispatcher/filters/magic_filters.html#regexp
    router.message.register(code_message, F.text.regexp(r"\d{7}", mode="fullmatch"))
    router.callback_query.register(callback_teacher_button_pressed, F.data.startswith("teacher_"))
    router.callback_query.register(callback_student_button_pressed, F.data.startswith("student_"))
    router.callback_query.register(callback_add_folder, F.data.startswith("add_"))
    router.callback_query.register(callback_delete_folder, F.data.startswith("delete_"))
    logging.info("register message handlers")
