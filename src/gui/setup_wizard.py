import tkinter as tk
from tkinter import messagebox
from .widgets.password_entry import PasswordEntry
from src.core.crypto.password_validator import PasswordValidator


class SetupWizard(tk.Toplevel):
    def __init__(self, parent, db, key_manager, on_finish):
        super().__init__(parent)
        self.title("Создание хранилища")
        self.geometry("450x400")
        self.db = db
        self.km = key_manager
        self.on_finish = on_finish

        tk.Label(self, text="Создание мастер-пароля", font=("Arial", 12)).pack(pady=20)
        tk.Label(self, text="Пароль:").pack()
        self.p1 = PasswordEntry(self)
        self.p1.pack(pady=5)

        tk.Label(self, text="Повторите:").pack()
        self.p2 = PasswordEntry(self)
        self.p2.pack(pady=5)

        tk.Button(self, text="Создать", command=self.finish).pack(pady=20)

    def finish(self):
        if self.p1.get() != self.p2.get():
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return

        ok, errs = PasswordValidator.validate(self.p1.get())
        if not ok:
            messagebox.showerror("Слабый пароль", "\n".join(errs))
            return

        # Создаём ключи и сохраняем
        keys = self.km.setup_new_user(self.p1.get())
        self.db.save_auth_data(keys['auth_hash'], keys['enc_salt'],
                               keys.get('audit_salt'), keys.get('export_salt'))

        # Вызываем callback и закрываем
        self.on_finish(self.p1.get(), "path")
        # НЕ вызываем self.destroy() здесь — это делает main.py
