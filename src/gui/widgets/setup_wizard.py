import tkinter as tk
from tkinter import messagebox, filedialog
from .widgets.password_entry import PasswordEntry


class SetupWizard(tk.Toplevel):
    """Мастер первоначальной настройки"""

    def __init__(self, parent, db, on_finish):
        super().__init__(parent)
        self.title("Первичная настройка CryptoSafe")
        self.geometry("450x400")
        self.db = db
        self.on_finish = on_finish

        # Запрет закрытия крестиком
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        tk.Label(self, text="Создание нового хранилища", font=("Arial", 14, "bold")).pack(pady=15)

        #Создание мастер-пароля
        f_pass = tk.LabelFrame(self, text="Безопасность", padx=10, pady=10)
        f_pass.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(f_pass, text="Мастер-пароль:").pack(anchor=tk.W)
        self.pass_entry = PasswordEntry(f_pass)
        self.pass_entry.pack(fill=tk.X, pady=2)

        tk.Label(f_pass, text="Подтверждение:").pack(anchor=tk.W)
        self.confirm_entry = PasswordEntry(f_pass)
        self.confirm_entry.pack(fill=tk.X, pady=2)

        #Выбор расположения БД
        f_loc = tk.LabelFrame(self, text="Хранилище данных", padx=10, pady=10)
        f_loc.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(f_loc, text="Путь к файлу базы данных:").pack(anchor=tk.W)
        self.path_var = tk.StringVar(value=self.db.db_path)
        tk.Entry(f_loc, textvariable=self.path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(f_loc, text="Обзор", command=self.browse_db).pack(side=tk.RIGHT, padx=5)

        #Настройки шифрования (заглушка)
        f_enc = tk.LabelFrame(self, text="Шифрование", padx=10, pady=10)
        f_enc.pack(fill=tk.X, padx=20, pady=5)


        tk.Button(self, text="Создать хранилище", command=self.finish, width=20).pack(pady=20)

    def browse_db(self):
        path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database", "*.db")])
        if path:
            self.path_var.set(path)

    def finish(self):
        p1 = self.pass_entry.get()
        p2 = self.confirm_entry.get()

        if len(p1) < 6:
            messagebox.showerror("Ошибка", "Пароль должен быть не менее 6 символов")
            return
        if p1 != p2:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return

        # Сохраняем параметры в БД (подготовка к Спринту 2)
        try:
            self.db.execute("INSERT INTO key_store (key_type, params) VALUES (?, ?)",
                            ("master", "created_sprint1"))
            print("[WIZARD] Настройки сохранены в key_store")
        except Exception as e:
            print(f"[WIZARD ERROR] {e}")

        self.on_finish(p1, self.path_var.get())
        self.destroy()

    def cancel(self):
        # Если пользователь закрыл окно
        self.on_finish(None, None)
        self.destroy()
