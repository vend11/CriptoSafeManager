import tkinter as tk
from tkinter import ttk, messagebox
from .widgets.password_entry import PasswordEntry
from src.core.crypto.password_validator import PasswordValidator
import threading


class ChangePasswordDialog(tk.Toplevel):
    def __init__(self, parent, db, key_manager):
        super().__init__(parent)
        self.title("Смена пароля")
        self.geometry("450x400")
        self.db, self.km = db, key_manager
        self.grab_set()

        tk.Label(self, text="Текущий пароль:").pack(anchor=tk.W, padx=20, pady=(20, 0))
        self.old = PasswordEntry(self);
        self.old.pack(padx=20, fill=tk.X)

        tk.Label(self, text="Новый пароль:").pack(anchor=tk.W, padx=20, pady=(10, 0))
        self.new = PasswordEntry(self);
        self.new.pack(padx=20, fill=tk.X)

        tk.Label(self, text="Повторите:").pack(anchor=tk.W, padx=20, pady=(10, 0))
        self.conf = PasswordEntry(self);
        self.conf.pack(padx=20, fill=tk.X)

        self.btn = tk.Button(self, text="Изменить", command=self.start);
        self.btn.pack(pady=20)
        self.pbar = ttk.Progressbar(self, mode='determinate');
        self.pbar.pack(fill=tk.X, padx=20)

    def start(self):
        if self.new.get() != self.conf.get(): return messagebox.showerror("Error", "Не совпадают")
        ok, errs = PasswordValidator.validate(self.new.get())
        if not ok: return messagebox.showerror("Weak", "\n".join(errs))

        data = self.db.get_auth_data()
        if not self.km.authenticate(self.old.get(), data['auth_hash'], data['enc_salt']):
            return messagebox.showerror("Error", "Старый пароль неверен")

        self.btn.config(state=tk.DISABLED)
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            old_key = self.km.get_session_key()
            new_keys = self.km.setup_new_user(self.new.get())
            new_key = self.km.get_session_key()

            ok = self.db.re_encrypt_all_data(old_key, new_key,
                                             lambda v: self.after(0, lambda: self.pbar.config(value=v)))
            if ok:
                self.db.save_auth_data(new_keys['auth_hash'], new_keys['enc_salt'])
                self.after(0, lambda: messagebox.showinfo("OK", "Пароль изменен"))
                self.after(0, self.destroy)
            else:
                raise Exception("DB Error")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self.btn.config(state=tk.NORMAL))
