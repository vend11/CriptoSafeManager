import tkinter as tk
from tkinter import ttk


class SecureTable(ttk.Treeview):
    """Таблица данных"""

    def __init__(self, parent, columns=("ID", "Title", "User", "URL"), **kwargs):
        super().__init__(parent, columns=columns, show='headings', **kwargs)

        self.column("ID", width=0, stretch=False)
        for col in columns[1:]:
            self.heading(col, text=col)
            self.column(col, width=150)

        self.pack(fill=tk.BOTH, expand=True)

    def update_data(self, data):
        self.delete(*self.get_children())
        for row in data:
            self.insert('', tk.END, values=row)
