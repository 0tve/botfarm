class BotfarmError(Exception):
    """Базовое кастомное исключение"""


class BotfarmDBError(BotfarmError):
    """Базовое исключение, связанное с БД"""


class BotfarmProjectError(BotfarmError):
    """Исключение, связанное с проектами"""


class BotfarmProjectNotExistsError(BotfarmProjectError):
    """Исключение, связанное с отсутствием проекта"""

    def __str__(self) -> str:
        return 'Указанный проект не существует'


class BotfarmUserError(BotfarmError):
    """Исключение, связанное с пользователями"""


class BotfarmUserNotExistsError(BotfarmUserError):
    """Исключение, связанное с отсутствием пользователя"""

    def __str__(self) -> str:
        return 'Указанный пользователь не существует'


class BotfarmUserLockedError(BotfarmUserError):
    """Исключение, связанное с занятым пользователем"""

    def __str__(self) -> str:
        return 'Указанный пользователь занят'
