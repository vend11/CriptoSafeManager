from PyQt6.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QLabel, QLineEdit, QFileDialog, QToolButton
from .password_entry import PasswordEntry

class SetupWizard(QWizard):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройка CryptoSafe")

        # Страница 1: Создание мастер-пароля
        self.addPage(self._create_password_page())
        # Страница 2: Выбор пути к БД
        self.addPage(self._create_db_page())
        # Страница 3: Заглушка шифрования
        self.addPage(self._create_crypto_page())

    def _create_password_page(self):
        page = QWizardPage()
        page.setTitle("Мастер-пароль")
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Создайте надежный мастер-пароль:"))

        self.pwd = PasswordEntry()  # Используем наш виджет из GUI-2
        self.confirm = PasswordEntry()

        layout.addWidget(self.pwd)
        layout.addWidget(QLabel("Подтвердите пароль:"))
        layout.addWidget(self.confirm)
        return page

    def _create_db_page(self):
        page = QWizardPage()
        page.setTitle("Расположение базы данных")
        layout = QVBoxLayout(page)
        self.db_path = QLineEdit("cryptosafe.db")
        btn = QToolButton()
        btn.setText("Обзор...")
        btn.clicked.connect(lambda: self.db_path.setText(QFileDialog.getSaveFileName()[0]))

        layout.addWidget(QLabel("Выберите, где хранить данные:"))
        layout.addWidget(self.db_path)
        return page

    def _create_crypto_page(self):
        page = QWizardPage()
        page.setTitle("Настройки шифрования")
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Параметры формирования ключа (Заглушка для Спринта 3)"))
        return page
