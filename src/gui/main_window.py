import sys
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QStatusBar, QMessageBox, QTableWidgetItem
from src.database.db import init_db, backup_placeholder
from src.core.events import emit  # EVT-1
from src.gui.widgets.secure_table import SecureTable
from src.gui.widgets.entry_dialog import EntryDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        init_db()

        self.setWindowTitle("CryptoSafe Manager")
        self.resize(1000, 600)

        # GUI-2: Таблица для записей
        self.table = SecureTable()
        self.setCentralWidget(self.table)

        # GUI-1: Строка состояния
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Статус: Разблокировано | Буфер: 00:00")

        self._build_menu()

    def _build_menu(self):
        mb = self.menuBar()

        # Меню Файл
        file_menu = mb.addMenu("Файл")
        # Привязываем создание записи к пункту "Создать"
        file_menu.addAction("Создать").triggered.connect(self._create_new_entry)
        file_menu.addAction("Открыть")
        file_menu.addAction("Резервная копия").triggered.connect(self._backup)
        file_menu.addAction("Выход").triggered.connect(self.close)

        # Меню Правка
        edit_menu = mb.addMenu("Правка")
        edit_menu.addAction("Добавить").triggered.connect(self._create_new_entry)
        edit_menu.addAction("Изменить")
        edit_menu.addAction("Удалить").triggered.connect(self._delete_entry)

        mb.addMenu("Вид")
        mb.addMenu("Справка")

    def _create_new_entry(self):
        """Логика создания новой записи согласно EVT-1"""
        dialog = EntryDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            # Валидация ввода (SEC-2)
            if not data['title']:
                QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
                return

            # Добавление в таблицу (визуализация)
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Заполнение колонок (ID, Название, Логин, URL, Дата, Теги)
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(data['title']))
            self.table.setItem(row, 2, QTableWidgetItem(data['login']))
            self.table.setItem(row, 3, QTableWidgetItem(data['url']))
            self.table.setItem(row, 4, QTableWidgetItem(datetime.now().strftime("%Y-%m-%d")))
            self.table.setItem(row, 5, QTableWidgetItem(data['tags']))

            # Публикация события в систему (EVT-1)
            emit("EntryAdded", data)
            self.statusBar().showMessage("Запись успешно создана", 3000)

    def _delete_entry(self):
        current_row = self.table.currentRow()
        if current_row != -1:
            self.table.removeRow(current_row)
            emit("EntryDeleted")  # EVT-1
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")

    def _backup(self):
        backup_placeholder()  # Исправлено: ссылка на DB-4
        QMessageBox.information(self, "Успех", "Резервная копия создана.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Здесь можно добавить вызов SetupWizard (GUI-3) перед основным окном
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
