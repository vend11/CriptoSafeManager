import tkinter as tk
from tkinter import ttk, messagebox


class LoginDialog(tk.Toplevel):
    def __init__(self, parent, key_manager):
        super().__init__(parent)
        self.title("Вход в хранилище")
        self.geometry("350x280")
        self.resizable(False, False)

        self.key_manager = key_manager
        self.success = False
        self.is_first_run = self._check_first_run()

        self.transient(parent)
        self.grab_set()

        if self.is_first_run:
            self.show_first_run_setup()
        else:
            self.create_widgets()
            self.center_window(parent)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window(self)

    def _check_first_run(self):
        """Проверяет, есть ли ключи в БД (первый запуск)"""
        try:
            auth_hash = self.key_manager.db.fetchone(
                "SELECT key_data FROM key_store WHERE key_type = 'auth_hash'"
            )
            enc_salt = self.key_manager.db.fetchone(
                "SELECT key_data FROM key_store WHERE key_type = 'enc_salt'"
            )
            return auth_hash is None or enc_salt is None
        except Exception:
            return True

    def create_widgets(self):
        """Создание интерфейса входа"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Введите мастер-пароль:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))

        self.password_entry = ttk.Entry(frame, show="*", width=30, font=("Arial", 11))
        self.password_entry.pack(fill=tk.X, pady=(0, 15))
        self.password_entry.bind("<Return>", self.on_login)
        self.password_entry.focus()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        self.login_btn = ttk.Button(btn_frame, text="🔓 Войти", command=self.on_login, width=12)
        self.login_btn.pack(side=tk.RIGHT, padx=5)

        ttk.Button(btn_frame, text="❌ Выход", command=self.on_cancel, width=12).pack(side=tk.RIGHT)

    def center_window(self, parent):
        """Центрирует окно на экране"""
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def on_login(self, event=None):
        """Обработчик входа"""
        # Проверка блокировки
        if self.key_manager.auth.is_locked_out():
            remaining = self.key_manager.auth.get_remaining_lockout_time()
            messagebox.showwarning(
                "Блокировка",
                f"Слишком много неудачных попыток.\nПодождите {remaining} сек.",
                parent=self
            )
            return

        password = self.password_entry.get()
        if not password:
            return

        try:
            self.login_btn.config(state=tk.DISABLED)

            if self.key_manager.unlock(password):
                self.success = True
                self.destroy()
            else:
                attempts = self.key_manager.auth.get_failed_attempts()
                max_attempts = self.key_manager.auth.get_max_attempts()
                remaining_attempts = max_attempts - attempts

                messagebox.showerror(
                    "Ошибка",
                    f"Неверный пароль.\n\n❌ Попыток: {attempts} из {max_attempts}\n"
                    f"⚡ Осталось: {remaining_attempts}",
                    parent=self
                )
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при входе: {e}", parent=self)
        finally:
            if self.winfo_exists():
                self.login_btn.config(state=tk.NORMAL)

    def show_first_run_setup(self):
        """Диалог создания нового пароля для первого запуска"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=" Добро пожаловать!", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        ttk.Label(
            frame,
            text="\nСоздайте мастер-пароль:",
            justify=tk.CENTER
        ).pack(pady=(0, 15))

        ttk.Label(frame, text="Новый пароль:").pack(anchor=tk.W)
        self.new_password = ttk.Entry(frame, show="*", width=30)
        self.new_password.pack(fill=tk.X, pady=(0, 5))

        # Индикатор сложности пароля
        self.strength_label = ttk.Label(frame, text="", font=("Arial", 8))
        self.strength_label.pack(anchor=tk.W, pady=(0, 10))
        self.new_password.bind("<KeyRelease>", self._check_password_strength)

        ttk.Label(frame, text="Подтверждение пароля:").pack(anchor=tk.W)
        self.confirm_password = ttk.Entry(frame, show="*", width=30)
        self.confirm_password.pack(fill=tk.X, pady=(0, 15))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        create_btn = ttk.Button(btn_frame, text="✅ Создать хранилище", command=self.create_vault)
        create_btn.pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="❌ Выход", command=self.on_cancel).pack(side=tk.RIGHT)

        self.new_password.bind("<Return>", lambda e: create_btn.invoke())
        self.confirm_password.bind("<Return>", lambda e: create_btn.invoke())
        self.new_password.focus()

        self.center_window(self.master)

    def _check_password_strength(self, event=None):
        """Проверка сложности пароля в реальном времени"""
        password = self.new_password.get()
        if len(password) == 0:
            self.strength_label.config(text="")
            return

        valid, msg = self.key_manager.auth.validate_password_strength(password)
        if valid:
            self.strength_label.config(text="✅ " + msg, foreground="green")
        else:
            self.strength_label.config(text="⚠️ " + msg, foreground="orange")

    def create_vault(self):
        """Создание нового хранилища с паролем"""
        password = self.new_password.get()
        confirm = self.confirm_password.get()

        if not password:
            messagebox.showwarning("Ошибка", "Введите пароль", parent=self)
            self.new_password.focus()
            return

        if password != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают", parent=self)
            self.new_password.delete(0, tk.END)
            self.confirm_password.delete(0, tk.END)
            self.new_password.focus()
            return

        # Проверка сложности пароля
        valid, msg = self.key_manager.auth.validate_password_strength(password)
        if not valid:
            messagebox.showerror(
                "Ошибка",
                f"Слабый пароль:\n{msg}\n\nПожалуйста, используйте более надежный пароль.",
                parent=self
            )
            return

        try:
            if self.key_manager.setup_new_vault(password):
                messagebox.showinfo(
                    "Успех",
                    "✅ Хранилище создано!\nТеперь войдите с новым паролем.",
                    parent=self
                )

                if self.key_manager.unlock(password):
                    self.success = True
                    self.destroy()
                else:
                    self.is_first_run = False
                    self.destroy()
                    self.__init__(self.master, self.key_manager)
            else:
                messagebox.showerror("Ошибка", "Не удалось создать хранилище", parent=self)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании: {e}", parent=self)

    def on_cancel(self):
        """Закрытие окна"""
        self.success = False
        self.destroy()
