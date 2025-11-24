import hashlib
import pathlib


def load_env(path: pathlib.Path) -> dict[str, str]:
    """Загружает пары ключ-значение из .env файла, игнорируя пустые строки и комментарии"""
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    env: dict[str, str] = {}

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        key, value = (part.strip() for part in line.split("=", 1))
        env[key] = value

    return env


def hash_password(password: str) -> str:
    """Возвращает SHA-256 хеш переданного пароля в шестнадцатеричном виде"""
    return hashlib.sha256(password.encode()).hexdigest()
