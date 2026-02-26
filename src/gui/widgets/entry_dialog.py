from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QDialogButtonBox
from .password_entry import PasswordEntry


class EntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить новую запись")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Поля ввода согласно структуре данных (Название, Логин, URL, Теги)
        self.title_input = QLineEdit()
        self.login_input = QLineEdit()
        self.url_input = QLineEdit()
        self.tags_input = QLineEdit()

        # Обязательный виджет согласно GUI-2
        self.password_input = PasswordEntry()

        form.addRow("Название:", self.title_input)
        form.addRow("Логин:", self.login_input)
        form.addRow("Пароль:", self.password_input)
        form.addRow("URL:", self.url_input)
        form.addRow("Теги:", self.tags_input)

        layout.addLayout(form)

        # Кнопки управления
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "title": self.title_input.text(),
            "login": self.login_input.text(),
            "password": self.password_input.text(),  # Получаем текст из виджета маскировки
            "url": self.url_input.text(),
            "tags": self.tags_input.text()
        }
