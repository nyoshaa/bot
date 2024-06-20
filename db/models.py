# __all__ - публичный список объектов
# https://ru.stackoverflow.com/questions/27983/%D0%A7%D1%82%D0%BE-%D1%82%D0%B0%D0%BA%D0%BE%D0%B5-all-%D0%B2-python

__all__ = [
    'User',
    'Folder',
    'Base',
]

import datetime
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, DATE, ForeignKey


# Декларативная модель базы данных
# https://metanit.com/python/database/3.2.php
class Base(DeclarativeBase):
    pass


class User(Base):
    """модель пользователя tg для регистрации и авторизации в яндекс диске (если преподаватель)"""

    __tablename__ = "user_table"

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)

    tg_id = Column(Integer, nullable=False, unique=True)

    tg_username = Column(String, nullable=False, unique=True)

    teacher_id = Column(Integer, ForeignKey("user_table.id"), nullable=True)

    yandex_api_token = Column(String, nullable=True, unique=True)


class Folder(Base):
    """модель папки с яндекс диска"""

    __tablename__ = "folder_table"

    folder_id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)

    user_tg_id = Column(Integer, ForeignKey('user_table.tg_id'))

    folder_path = Column(String, unique=True, nullable=False)
