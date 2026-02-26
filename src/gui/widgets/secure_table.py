from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView


class SecureTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.headers = ["ID", "Название", "Логин", "URL", "Дата создания", "Теги"]
        self.setColumnCount(len(self.headers))
        self.setHorizontalHeaderLabels(self.headers)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.add_test_data()

    def add_test_data(self):
        test_entries = [
            ("1", "Google", "user@gmail.com", "google.com", "2024-05-20", "work"),
            ("2", "GitHub", "dev_admin", "github.com", "2024-05-21", "dev")
        ]
        self.setRowCount(len(test_entries))
        for row, data in enumerate(test_entries):
            for col, value in enumerate(data):
                self.setItem(row, col, QTableWidgetItem(value))
