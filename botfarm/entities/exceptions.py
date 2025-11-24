class BotfarmError(Exception):
    """Базовое кастомное исключение"""

class BotfarmDBError(BotfarmError):
    """Базовое исключение, связанное с БД"""