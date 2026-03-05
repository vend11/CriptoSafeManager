import tkinter as tk
from tkinter import ttk

class SettingsDialog(tk.Toplevel):
    """Диалог настроек"""
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("Настройки")
        self.geometry("500x400")
        self.config = config

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка Безопасность
        sec_frame = tk.Frame(notebook)
        notebook.add(sec_frame, text="Безопасность")
        tk.Label(sec_frame, text="Таймаут буфера обмена (сек):").pack(pady=5)
        tk.Entry(sec_frame).pack(pady=5)
        tk.Label(sec_frame, text="Авто-блокировка (мин):").pack(pady=5)
        tk.Entry(sec_frame).pack(pady=5)

        # Вкладка Внешний вид
        app_frame = tk.Frame(notebook)
        notebook.add(app_frame, text="Внешний вид")
        tk.Label(app_frame, text="Тема:").pack(pady=5)
        tk.Combobox(app_frame, values=["Light", "Dark"]).pack(pady=5)

        # Вкладка Дополнительно
        adv_frame = tk.Frame(notebook)
        notebook.add(adv_frame, text="Дополнительно")
        tk.Label(adv_frame, text="Путь к резервным копиям:").pack(pady=5)
        tk.Entry(adv_frame).pack(pady=5)
