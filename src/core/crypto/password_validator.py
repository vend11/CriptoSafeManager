import re
from typing import List, Tuple


class PasswordValidator:
    MIN_LENGTH = 12

    @staticmethod
    def validate(password: str) -> Tuple[bool, List[str]]:
        errors = []
        if len(password) < PasswordValidator.MIN_LENGTH:
            errors.append(f"Минимум {PasswordValidator.MIN_LENGTH} символов.")
        if not re.search(r'[A-Z]', password): errors.append("Добавьте заглавные буквы.")
        if not re.search(r'[a-z]', password): errors.append("Добавьте строчные буквы.")
        if not re.search(r'[0-9]', password): errors.append("Добавьте цифры.")
        if not re.search(r'[^A-Za-z0-9]', password): errors.append("Добавьте спецсимволы.")

        common = ["password", "123456", "qwerty"]
        if any(p in password.lower() for p in common):
            errors.append("Слишком простой пароль.")

        return len(errors) == 0, errors
