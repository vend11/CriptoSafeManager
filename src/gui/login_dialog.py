import tkinter as tk
from tkinter import messagebox
from .widgets.password_entry import PasswordEntry
import math


class LoginDialog(tk.Toplevel):
    def __init__(self, parent, db, key_manager, on_success):
        super().__init__(parent)
        self.title("Вход")
        self.geometry("400x250")
        self.db, self.km, self.on_success = db, key_manager, on_success
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._lock_job = None

        tk.Label(self, text="Мастер-пароль", font=("Arial", 12)).pack(pady=20)

        self.pass_entry = PasswordEntry(self, width=30)
        self.pass_entry.pack(pady=10)
        self.pass_entry.entry.bind("<Return>", self.try_login)

        self.btn_login = tk.Button(self, text="Войти", command=self.try_login, width=20)
        self.btn_login.pack(pady=20)

        self.status = tk.Label(self, text="", fg="red")
        self.status.pack()

    def try_login(self, ev=None):
        if str(self.pass_entry.entry.cget('state')) == 'disabled':
            return

        p = self.pass_entry.get()
        if not p:
            self.status.config(text="Введите пароль", fg="orange")
            return

        data = self.db.get_auth_data()
        if self.km.authenticate(p, data['auth_hash'], data['enc_salt']):
            self.on_success(True)
            self.destroy()
        else:
            remaining = self.km.get_remaining_lock_time()
            if remaining > 0:
                self._start_lockout(remaining)
            else:
                self.status.config(text="Неверный пароль", fg="red")

    def _start_lockout(self, seconds):
        self.pass_entry.entry.config(state=tk.DISABLED)
        self.btn_login.config(state=tk.DISABLED)
        self._update_lockout_label(math.ceil(seconds))

    def _update_lockout_label(self, secs_left):
        if secs_left > 0:
            self.status.config(text=f"Слишком много попыток. Повторите через {secs_left} сек.", fg="red")
            self._lock_job = self.after(1000, lambda: self._update_lockout_label(secs_left - 1))
        else:
            self.pass_entry.entry.config(state=tk.NORMAL)
            self.btn_login.config(state=tk.NORMAL)
            self.status.config(text="Попробуйте снова", fg="orange")
            self.pass_entry.entry.focus_set()
            self._lock_job = None

    def _on_close(self):
        if self._lock_job is not None:
            self.after_cancel(self._lock_job)
        self.on_success(False)
        self.destroy()
