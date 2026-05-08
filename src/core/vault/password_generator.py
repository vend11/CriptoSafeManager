import secrets
import string
import logging
import re
from typing import Optional, Set, List
from collections import deque

logger = logging.getLogger("PasswordGenerator")

# Наборы символов
UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

# Неоднозначные символы для исключения
AMBIGUOUS_CHARS = set("lI10Oo")

MIN_LENGTH = 8
MAX_LENGTH = 64
DEFAULT_LENGTH = 16

DEFAULT_HISTORY_SIZE = 20


class PasswordStrength:
    @staticmethod
    def calculate(password: str) -> int:
        if not password:
            return 0
        score = 0
        length = len(password)

        if length >= 8:
            score += 1
        if length >= 12:
            score += 1
        if length >= 16:
            score += 1
        char_types = 0
        if re.search(r'[A-Z]', password):
            char_types += 1
        if re.search(r'[a-z]', password):
            char_types += 1
        if re.search(r'[0-9]', password):
            char_types += 1
        if re.search(r'[^A-Za-z0-9]', password):
            char_types += 1

        if char_types >= 3:
            score += 1

        return min(score, 4)

    @staticmethod
    def get_label(score: int) -> str:
        labels = ["Очень слабый", "Слабый", "Средний", "Сильный", "Очень сильный"]
        return labels[score] if 0 <= score <= 4 else "Unknown"


class PasswordGenerator:
    def __init__(self, history_size: int = DEFAULT_HISTORY_SIZE):
        self._history: deque = deque(maxlen=history_size)
    def generate(
        self,
        length: int = DEFAULT_LENGTH,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        exclude_ambiguous: bool = False,
    ) -> str:
        length = max(MIN_LENGTH, min(MAX_LENGTH, length))
        charset = ""
        required_chars = []

        if use_uppercase:
            chars = UPPERCASE
            if exclude_ambiguous:
                chars = self._exclude(chars, AMBIGUOUS_CHARS)
            charset += chars
            required_chars.append(self._safe_choice(chars))

        if use_lowercase:
            chars = LOWERCASE
            if exclude_ambiguous:
                chars = self._exclude(chars, AMBIGUOUS_CHARS)
            charset += chars
            required_chars.append(self._safe_choice(chars))

        if use_digits:
            chars = DIGITS
            if exclude_ambiguous:
                chars = self._exclude(chars, AMBIGUOUS_CHARS)
            charset += chars
            required_chars.append(self._safe_choice(chars))

        if use_symbols:
            chars = SYMBOLS
            if exclude_ambiguous:
                chars = self._exclude(chars, AMBIGUOUS_CHARS)
            charset += chars
            required_chars.append(self._safe_choice(chars))

        if not charset:
            raise ValueError("Не выбран ни один набор символов для генерации пароля")
        password_chars = list(required_chars)
        remaining = length - len(password_chars)
        for _ in range(max(0, remaining)):
            password_chars.append(self._safe_choice(charset))

        # Перемешиваем
        password = self._shuffle(password_chars)

        #Проверка на дубликаты в истории
        if password in self._history:
            return self.generate(length, use_uppercase, use_lowercase,
                                 use_digits, use_symbols, exclude_ambiguous)
        self._history.append(password)
        logger.debug(f"Generated password: length={length}, strength={PasswordStrength.calculate(password)}")
        return password

    def get_strength(self, password: str) -> tuple:
        """Получить оценку сложности пароля"""
        score = PasswordStrength.calculate(password)
        return score, PasswordStrength.get_label(score)

    def get_history(self) -> List[str]:
        """Получить историю паролей"""
        return list(self._history)

    def clear_history(self):
        """Очистить историю паролей."""
        self._history.clear()

    @staticmethod
    def _safe_choice(charset: str) -> str:
        if not charset:
            raise ValueError("Charset is empty")
        idx = secrets.randbelow(len(charset))
        return charset[idx]

    @staticmethod
    def _shuffle(chars: list) -> str:
        arr = chars[:]
        for i in range(len(arr) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            arr[i], arr[j] = arr[j], arr[i]
        return ''.join(arr)

    @staticmethod
    def _exclude(charset: str, exclude: Set[str]) -> str:
        return ''.join(c for c in charset if c not in exclude)
