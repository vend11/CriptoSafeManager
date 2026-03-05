import tkinter as tk


class PasswordEntry(tk.Frame):
    """Поле пароля с кнопкой 'глаз'"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.var = tk.StringVar()

        self.entry = tk.Entry(self, textvariable=self.var, show="*", **kwargs)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn = tk.Button(self, text="👁", width=3, command=self.toggle)
        self.btn.pack(side=tk.RIGHT)

    def toggle(self):
        if self.entry.cget('show') == '*':
            self.entry.config(show='')
            self.btn.config(text="🔒")
        else:
            self.entry.config(show='*')
            self.btn.config(text="👁")

    def get(self):
        return self.var.get()
