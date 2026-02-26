from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QToolButton


class PasswordEntry(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.edit = QLineEdit()
        self.edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn = QToolButton()
        self.btn.setText("👁")
        self.btn.clicked.connect(self.toggle_password)

        layout.addWidget(self.edit)
        layout.addWidget(self.btn)

    def toggle_password(self):
        if self.edit.echoMode() == QLineEdit.EchoMode.Password:
            self.edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.edit.setEchoMode(QLineEdit.EchoMode.Password)

    def text(self):
        return self.edit.text()
