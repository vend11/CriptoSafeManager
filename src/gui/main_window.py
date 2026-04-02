import tkinter as tk
from tkinter import messagebox
from .widgets.secure_table import SecureTable
from .widgets.audit_log_viewer import AuditLogViewer
from .settings_dialog import SettingsDialog
from .change_password_dialog import ChangePasswordDialog


class MainWindow(tk.Tk):
    def __init__(self, config, state, db, events, key_manager=None):
        super().__init__()
        self.title("CryptoSafe Manager")
        self.geometry("900x600")
        self.app_config, self.state, self.db, self.events, self.km = config, state, db, events, key_manager
        self._create_menu();
        self._create_main_area();
        self._create_status_bar()
        self.after(100, self._check_first_run)

        self.bind_all("<Key>", self._activity);
        self.bind_all("<Button>", self._activity)
        self.bind("<Unmap>", self._minimized)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _activity(self, e):
        if self.km: self.km.storage.update_activity()

    def _minimized(self, e):
        if self.state() == 'iconic' and self.km:
            self.km.clear_session_key()
            self.status_var.set("Заблокировано (свернуто)")

    def _on_close(self):
        if self.km: self.km.clear_session_key()
        self.destroy()

    def _create_menu(self):
        m = tk.Menu(self)
        f = tk.Menu(m, tearoff=0);
        f.add_command(label="Бэкап", command=lambda: self.db.create_backup());
        f.add_separator();
        f.add_command(label="Выход", command=self._on_close)
        m.add_cascade(label="Файл", menu=f)
        ed = tk.Menu(m, tearoff=0);
        ed.add_command(label="Добавить", command=self.add);
        ed.add_command(label="Удалить", command=self.delete);
        ed.add_separator();
        ed.add_command(label="Сменить пароль", command=self._change_pass)
        m.add_cascade(label="Правка", menu=ed)
        vw = tk.Menu(m, tearoff=0);
        vw.add_command(label="Логи", command=lambda: AuditLogViewer(self));
        vw.add_command(label="Настройки", command=lambda: SettingsDialog(self, self.app_config))
        m.add_cascade(label="Вид", menu=vw)
        self.config(menu=m)

    def _create_main_area(self):
        self.table = SecureTable(self);
        self.table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.refresh_table()

    def _create_status_bar(self):
        self.status_var = tk.StringVar(value="Статус: Готов")
        tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM,
                                                                                               fill=tk.X)

    def _check_first_run(self):
        pass

    def add(self):
        self.db.add_vault_entry("New", "user", "pass");
        self.refresh_table()

    def delete(self):
        if not self.table.selection(): return
        iid = self.table.item(self.table.selection()[0])['values'][0]
        self.db.delete_entry(iid);
        self.refresh_table()

    def refresh_table(self):
        rs = self.db.fetch_all("SELECT id, title, username, url FROM vault_entries")
        self.table.update_data([(r['id'], r['title'], r['username'], r['url']) for r in rs])

    def _change_pass(self):
        ChangePasswordDialog(self, self.db, self.km)
