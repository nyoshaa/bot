from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_keyboard_select_path(paths: list[str], action: str) -> InlineKeyboardMarkup:
    """
    Сгенерировать клавиатуру для выбора пути (при удалении или добавлении).

    Args:
        paths (list[str]): Список путей, которые отобразятся как кнопки.
        action (str): add (добавление) или delete (удаление). Определяет callback_data кнопки

    Возвращает:
        InlineKeyboardMarkup: Клавиатура.
    """
    buttons = []
    for path in paths:
        button = InlineKeyboardButton(
            text=path,
            callback_data=action + "_" + path + "_button_pressed",
        )
        buttons.append([button])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# кнопки для клавиатуры выбора типа пользователя
teacher_button = InlineKeyboardButton(
    text="Преподаватель",
    callback_data="teacher_button_pressed",
)
student_button = InlineKeyboardButton(
    text="Студент",
    callback_data="student_button_pressed",
)
# клавиатура выбора типа пользователя
keyboard_teacher_or_student = InlineKeyboardMarkup(
    inline_keyboard=[[teacher_button], [student_button]]
)
