import tkinter as tk
from tkinter import ttk

class SettingsDialog(tk.Toplevel):
    """Диалог настроек"""
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("Настройки")
        self.geometry("500x350")
        self.config = config
        
        # Запрещаем взаимодействие с главным окном, пока открыты настройки
        self.grab_set()
        
        self._create_widgets()
        self._load_settings()

    def _create_widgets(self):
        # Создаем вкладки
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Вкладка Безопасность ---
        sec_frame = tk.Frame(notebook)
        notebook.add(sec_frame, text="Безопасность")
        
        # Поле: Таймаут буфера обмена
        tk.Label(sec_frame, text="Очистка буфера обмена (сек):").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.clipboard_entry = tk.Entry(sec_frame)
        self.clipboard_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # Поле: Авто-блокировка
        tk.Label(sec_frame, text="Авто-блокировка (минуты):").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.lock_entry = tk.Entry(sec_frame)
        self.lock_entry.pack(fill=tk.X, padx=10, pady=5)

        # --- Вкладка Внешний вид ---
        app_frame = tk.Frame(notebook)
        notebook.add(app_frame, text="Внешний вид")
        
        tk.Label(app_frame, text="Тема:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.theme_combo = ttk.Combobox(app_frame, values=["Light", "Dark"], state="readonly")
        self.theme_combo.pack(fill=tk.X, padx=10, pady=5)

        # --- Кнопки ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Button(btn_frame, text="Сохранить", command=self._save_settings).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.RIGHT)

    def _load_settings(self):
        """Загружаем текущие настройки в поля вводода."""
        # Получаем значения из ConfigManager (или дефолтные)
        clip_val = self.config.get('clipboard_timeout', 30)
        lock_val = self.config.get('auto_lock_timeout', 300)
        
        self.clipboard_entry.insert(0, str(clip_val))
        # Переводим секунды в минуты для удобства пользователя
        self.lock_entry.insert(0, str(lock_val // 60))

    def _save_settings(self):
        """Сохраняем настройки через ConfigManager."""
        try:
            # Валидация данных
            clip_val = int(self.clipboard_entry.get())
            lock_min = int(self.lock_entry.get())
            
            # Сохраняем в конфиг (это автоматически запишет в БД благодаря нашему ConfigManager)
            self.config.set('clipboard_timeout', clip_val)
            self.config.set('auto_lock_timeout', lock_min * 60)
            
            tk.messagebox.showinfo("Успех", "Настройки сохранены", parent=self)
            self.destroy()
            
        except ValueError:
            tk.messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа", parent=self)
