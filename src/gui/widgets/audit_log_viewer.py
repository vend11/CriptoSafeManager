import tkinter as tk
from tkinter import ttk


class AuditLogViewer(tk.Toplevel):
    """Окно логов (Заглушка Спринт 5)."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Логи аудита")
        self.geometry("500x300")

        tk.Label(self, text="Здесь будут логи (Спринт 5)").pack(pady=20)

        cols = ("Time", "Action")
        tree = ttk.Treeview(self, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
        tree.pack(fill=tk.BOTH, expand=True)
