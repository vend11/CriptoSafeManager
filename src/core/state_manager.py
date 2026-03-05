from src.core.events import EventSystem, Events


class StateManager:
    def __init__(self, event_system: EventSystem):
        self.events = event_system
        self.is_locked = True
        self.current_user = None
        self.clipboard_content = None
        self.clipboard_timer_id = None
        # Хранит время последнего действия
        self.last_activity_time = None
        # Счетчик секунд бездействия
        self.inactivity_seconds = 0
        self._setup_listeners()

    def _setup_listeners(self):
        """Подписка на события изменения состояния."""
        self.events.subscribe(Events.USER_LOGGED_IN, self._on_login)
        self.events.subscribe(Events.USER_LOGGED_OUT, self._on_logout)

    def _on_login(self, data):
        user = data if isinstance(data, str) else data.get('username', 'Unknown')
        self.login(user)

    def _on_logout(self, data):
        self.logout()

    def login(self, username):
        print(f"[STATE] Пользователь вошел: {username}")
        self.is_locked = False
        self.current_user = username
        # Сбрасываем таймеры
        self.reset_activity()

    def logout(self):
        """выход/блокировка."""
        print("[STATE] Сессия завершена (logout)")
        self.is_locked = True
        self.current_user = None

        #очищаем чувствительные данные из памяти
        self.clipboard_content = None
        self.inactivity_seconds = 0

        # Отменяем активные таймеры, если есть
        self.clipboard_timer_id = None

    def reset_activity(self):
        import time
        self.last_activity_time = time.time()
        self.inactivity_seconds = 0
