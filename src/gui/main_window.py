import tkinter as tk
import time
from .widgets.secure_table import SecureTable
from .widgets.audit_log_viewer import AuditLogViewer
from .settings_dialog import SettingsDialog
from .change_password_dialog import ChangePasswordDialog


class MainWindow(tk.Toplevel):
    def __init__(self, parent, config, state, db, events, key_manager=None):
        super().__init__(parent)
        self.title("CryptoSafe Manager")
        self.geometry("900x600")
        self.app_config = config
        self.state = state
        self.db = db
        self.events = events
        self.km = key_manager

        self._create_menu()
        self._create_main_area()
        self._create_status_bar()
        self._update_session_status()

        self.after(2000, self._periodic_update_status)

        self.bind_all("<Key>", self._activity)
        self.bind_all("<Button>", self._activity)
        self.bind("<Unmap>", self._minimized)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _activity(self, event=None):
        if self.state:
            self.state.reset_activity()
        if self.km and hasattr(self.km.storage, 'update_activity'):
            self.km.storage.update_activity()
        self._update_session_status()

    def _minimized(self, event=None):
        if self.state:
            self.state.is_locked = True
        if self.km:
            self.km.clear_session_key()
        self._update_session_status()

    def _on_close(self):
        if self.km:
            self.km.clear_session_key()
        if self.state:
            self.state.logout()
        self.destroy()

    def _create_menu(self):
        m = tk.Menu(self)
        f = tk.Menu(m, tearoff=0)
        f.add_command(label="Бэкап", command=lambda: self.db.create_backup())
        f.add_separator()
        f.add_command(label="Выход", command=self._on_close)
        m.add_cascade(label="Файл", menu=f)

        ed = tk.Menu(m, tearoff=0)
        ed.add_command(label="Добавить", command=self.add)
        ed.add_command(label="Удалить", command=self.delete)
        ed.add_separator()
        ed.add_command(label="Сменить пароль", command=self._change_pass)
        m.add_cascade(label="Правка", menu=ed)

        vw = tk.Menu(m, tearoff=0)
        vw.add_command(label="Логи", command=lambda: AuditLogViewer(self))
        vw.add_command(label="Настройки", command=lambda: SettingsDialog(self, self.app_config))
        m.add_cascade(label="Вид", menu=vw)

        self.config(menu=m)

    def _create_main_area(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.table = SecureTable(main_frame)
        self.table.pack(fill=tk.BOTH, expand=True)
        self.refresh_table()

    def _create_status_bar(self):
        self.status_var = tk.StringVar(value="Статус: Готов")
        tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    def _update_session_status(self):
        if not self.state or self.state.is_locked or not self.state.current_user:
            self.status_var.set("Статус: Заблокировано")
            return

        info = self.state.get_session_info()
        duration = self.state.get_session_duration()

        login_str = (
            time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(info["login_time"]))
            if info["login_time"] else "—"
        )

        text = (
            f"Вход: {login_str} | "
            f"Сессия: {duration} | "
            f"Неудачных попыток: {info['failed_attempts']}"
        )
        self.status_var.set(text)

    def _periodic_update_status(self):
        self._update_session_status()
        self.after(2000, self._periodic_update_status)

    def add(self):
        self.db.add_vault_entry("New", "user", "pass")
        self.refresh_table()

    def delete(self):
        if not self.table.selection():
            return
        iid = self.table.item(self.table.selection()[0])['values'][0]
        self.db.delete_entry(iid)
        self.refresh_table()

    def refresh_table(self):
        rs = self.db.fetch_all("SELECT id, title, username, url FROM vault_entries")
        self.table.update_data([(r['id'], r['title'], r['username'], r['url']) for r in rs])

    def _change_pass(self):
        ChangePasswordDialog(self, self.db, self.km)
