import tkinter as tk
from tkinter import ttk
from datetime import datetime
import time


class SessionInfoPanel(ttk.LabelFrame):
    """Панель с информацией о сессии для главного окна"""

    def __init__(self, parent, key_manager, **kwargs):
        super().__init__(parent, text="📊 Информация о сессии", padding=10, **kwargs)
        self.key_manager = key_manager
        self.update_id = None

        self._create_widgets()
        self._start_updates()

    def _create_widgets(self):
        """Создание виджетов панели"""
        # Статус
        self.status_label = ttk.Label(self, text="Статус: 🟢 Активна", font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky="w", pady=2)

        # Иконка замка
        self.lock_icon = ttk.Label(self, text="🔓", font=("Arial", 14))
        self.lock_icon.grid(row=0, column=1, rowspan=2, padx=(20, 0), sticky="e")

        # Время входа
        self.login_time_label = ttk.Label(self, text="Время входа: --:--:--", font=("Arial", 9))
        self.login_time_label.grid(row=1, column=0, sticky="w", pady=2)

        # Длительность сессии
        self.duration_label = ttk.Label(self, text="Длительность: 00:00:00", font=("Arial", 9))
        self.duration_label.grid(row=2, column=0, sticky="w", pady=2)

        # Авто-блокировка
        self.auto_lock_label = ttk.Label(self, text="Авто-блокировка: через --:--", font=("Arial", 9))
        self.auto_lock_label.grid(row=3, column=0, sticky="w", pady=2)

        # Неудачные попытки (история)
        self.failed_label = ttk.Label(self, text="❌ Неудачных попыток входа: 0", font=("Arial", 9))
        self.failed_label.grid(row=4, column=0, sticky="w", pady=2)

        # Кнопка блокировки
        self.lock_button = ttk.Button(self, text="🔒 Заблокировать", command=self._on_lock_button)
        self.lock_button.grid(row=0, column=2, rowspan=3, padx=(20, 0), sticky="e")

        # Кнопка смены пароля
        self.change_password_button = ttk.Button(
            self,
            text="🔄 Сменить пароль",
            command=self._on_change_password
        )
        self.change_password_button.grid(row=2, column=2, rowspan=2, padx=(20, 0), sticky="e")

        # Разделитель
        separator = ttk.Separator(self, orient='horizontal')
        separator.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        # Настройка весов колонок
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)

    def _update_info(self):
        """Обновление информации на панели"""
        if not self.key_manager.auth.is_session_active():
            # Если сессия не активна, показываем сообщение
            self.status_label.config(text="Статус: ⚪ Не активна", foreground="gray")
            self.lock_icon.config(text="🔒")
            self.login_time_label.config(text="Время входа: --:--:--")
            self.duration_label.config(text="Длительность: 00:00:00")
            self.auto_lock_label.config(text="Авто-блокировка: --:--")
            return

        # Получаем информацию о сессии
        login_time = self.key_manager.auth.get_session_login_time()
        if login_time:
            login_datetime = datetime.fromtimestamp(login_time)

            # Длительность сессии
            elapsed = self.key_manager.auth.get_session_duration()
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)

            # Время до авто-блокировки
            remaining_idle = self.key_manager.auth.get_remaining_idle_time()
            remaining_min = int(remaining_idle // 60)
            remaining_sec = int(remaining_idle % 60)

            # Получаем количество неудачных попыток (из истории)
            failed_attempts = self.key_manager.auth.get_failed_attempts()

            # Обновляем метки
            self.status_label.config(text="Статус: 🟢 Активна", foreground="green")
            self.lock_icon.config(text="🔓")
            self.login_time_label.config(
                text=f"Время входа: {login_datetime.strftime('%H:%M:%S')} ({login_datetime.strftime('%d.%m.%Y')})"
            )
            self.duration_label.config(text=f"Длительность: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.auto_lock_label.config(text=f"Авто-блокировка: через {remaining_min:02d}:{remaining_sec:02d}")

            # Цвет для неудачных попыток
            if failed_attempts > 0:
                self.failed_label.config(
                    text=f"❌ Неудачных попыток входа: {failed_attempts}",
                    foreground="orange"
                )
            else:
                self.failed_label.config(
                    text=f"❌ Неудачных попыток входа: {failed_attempts}",
                    foreground="gray"
                )

    def _start_updates(self):
        """Запуск периодического обновления"""

        def update_loop():
            if self.winfo_exists():
                self._update_info()
                # Обновляем каждую секунду
                self.update_id = self.after(1000, update_loop)

        self.update_id = self.after(1000, update_loop)

    def _on_lock_button(self):
        """Обработчик кнопки блокировки"""
        self.key_manager.lock()
        # Обновляем UI
        self._update_info()
        # Показываем диалог входа заново
        self._show_login_dialog()

    def _show_login_dialog(self):
        """Показывает диалог входа после блокировки"""
        from .login_dialog import LoginDialog  # Импортируем здесь, чтобы избежать циклической зависимости

        # Получаем родительское окно
        root = self.winfo_toplevel()

        # Скрываем главное окно
        root.withdraw()

        # Показываем диалог входа
        login_dialog = LoginDialog(root, self.key_manager)

        if login_dialog.success:
            # Вход успешен - показываем главное окно
            root.deiconify()
            self._update_info()
        else:
            # Вход отменен - закрываем приложение
            root.quit()

    def _on_change_password(self):
        """Обработчик смены пароля"""
        self._show_change_password_dialog()

    def _show_change_password_dialog(self):
        """Показывает диалог смены пароля"""
        from .change_password_dialog import ChangePasswordDialog

        dialog = ChangePasswordDialog(self.winfo_toplevel(), self.key_manager)
        if dialog.success:
            self._update_info()

    def destroy(self):
        """Очистка при закрытии"""
        if self.update_id:
            self.after_cancel(self.update_id)
        super().destroy()
