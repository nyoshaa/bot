import logging
from aiogram.types import CallbackQuery
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from db import async_session_maker, User, Folder


# Callback_query_handler - это функция, которая позволяет обрабатывать коллбек-запросы от пользователей.
# Коллбэк-запрос - это запрос, который отправляется боту, когда пользователь нажимает кнопку в его чате.
# Обработчик для callback с F.data для aiogram3
# https://ru.stackoverflow.com/questions/1565436/%D0%9A%D0%B0%D0%BA-%D1%81%D0%B4%D0%B5%D0%BB%D0%B0%D1%82%D1%8C-%D0%BE%D0%B1%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA-%D0%BA%D0%BE%D0%BB%D0%B1%D0%B5%D0%BA%D0%BE%D0%B2-%D0%B2-aiogram-3


async def callback_add_folder(callback: CallbackQuery):
    """добавить папку"""
    async with async_session_maker() as session:
        session: AsyncSession
        data = callback.data.split("_")
        folder_path = data[1]
        insert_folder_stmt = insert(Folder).values(user_tg_id=callback.from_user.id, folder_path=folder_path)
        await session.execute(insert_folder_stmt)
        await session.commit()

    await callback.message.answer("Папка добавлена!")
    logging.info(f"user {callback.from_user.id} pressed add folder button")

async def callback_delete_folder(callback: CallbackQuery):
    """удалить папку"""
    async with async_session_maker() as session:
        session: AsyncSession
        data = callback.data.split("_")
        folder_path = data[1]
        delete_folder_stmt = delete(Folder).where(Folder.user_tg_id == callback.from_user.id, Folder.folder_path == folder_path)
        await session.execute(delete_folder_stmt)
        await session.commit()

    await callback.message.answer("Папка удалена!")
    logging.info(f"user {callback.from_user.id} pressed delete folder button")

async def callback_teacher_button_pressed(callback: CallbackQuery):
    """кнопка преподавателя"""
    await callback.message.answer("Отлично! Регистрация почти завершена. Введите /register для получения токена Яндекс.Диска")
    logging.info(f"user {callback.from_user.id} pressed teacher button")

async def callback_student_button_pressed(callback: CallbackQuery):
    """кнопка студента"""
    await callback.message.answer("Отлично! Регистрация почти завершена. Попросите у преподавателя ссылку, чтобы вы могли отслеживать изменения на его диске.")
    logging.info(f"user {callback.from_user.id} pressed student button")
