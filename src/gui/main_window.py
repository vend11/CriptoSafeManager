import tkinter as tk
from tkinter import messagebox
from .widgets.secure_table import SecureTable
from .widgets.audit_log_viewer import AuditLogViewer
from .settings_dialog import SettingsDialog
from .setup_wizard import SetupWizard


class MainWindow(tk.Tk):
    def __init__(self, config, state, db, events):
        super().__init__()
        self.title("CryptoSafe Manager")
        self.geometry("900x600")

        self.app_config = config
        self.state = state
        self.db = db
        self.events = events

        self._create_menu()
        self._create_main_area()
        self._create_status_bar()

        self.after(100, self._check_first_run)

    def _create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self)

        #Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Создать", command=self.not_implemented)
        file_menu.add_command(label="Открыть", command=self.not_implemented)
        file_menu.add_command(label="Резервная копия", command=self.create_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        #Меню Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Добавить", command=self.add_entry_dialog)
        edit_menu.add_command(label="Изменить", command=self.not_implemented)
        edit_menu.add_command(label="Удалить", command=self.not_implemented)
        menubar.add_cascade(label="Правка", menu=edit_menu)

        #Меню Вид
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Логи аудита", command=self.show_logs)
        view_menu.add_command(label="Настройки", command=self.show_settings)
        menubar.add_cascade(label="Вид", menu=view_menu)

        #Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menubar)

    def _create_main_area(self):
        #Центральный виджет таблицы
        self.table = SecureTable(self)
        self.table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.refresh_table()

    def _create_status_bar(self):
        #Строка состояния с таймером
        self.status_var = tk.StringVar()
        # Заглушка таймера буфера обмена
        self.status_var.set("Статус: Заблокировано | Буфер: Очищен (00с)")
        status = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)

    def _check_first_run(self):
        # Проверяем, есть ли ключи
        keys = self.db.fetch_all("SELECT id FROM key_store")
        if not keys:
            # Передаем db в мастер настройки, чтобы он мог сохранить состояние
            wizard = SetupWizard(self, self.db, self._on_setup_complete)
            wizard.grab_set()
        else:
            self.status_var.set("Статус: Готов | Буфер: --")

    def _on_setup_complete(self, password, db_path):
        if password:
            self.status_var.set("Статус: Разблокировано | Буфер: Активен")
            self.events.publish("UserLoggedIn", "admin")
            messagebox.showinfo("Успех", "Хранилище успешно создано!")
        else:
            self.quit()

    def add_entry_dialog(self):
        # Диалог добавления (заглушка)
        self.db.add_vault_entry("New Entry", "user", "password123", "http://url.com")
        self.refresh_table()
        self.events.publish("EntryAdded", "New Entry")

    def refresh_table(self):
        rows = self.db.fetch_all("SELECT id, title, username, url FROM vault_entries")
        data = [(r['id'], r['title'], r['username'], r['url']) for r in rows]
        self.table.update_data(data)

    def create_backup(self):
        path = self.db.create_backup()
        if path:
            messagebox.showinfo("Резервная копия", f"Сохранено в:\n{path}")

    def show_logs(self):
        AuditLogViewer(self)

    def show_settings(self):
        SettingsDialog(self, self.app_config)

    def show_about(self):
        messagebox.showinfo("О программе", "CryptoSafe Manager v1.0\nСпринт 1")

    def not_implemented(self):
        messagebox.showinfo("Информация", "Функционал в разработке (будущие спринты)")
