from src.core.events import EventSystem, Events

class StateManager:
    def __init__(self, event_system: EventSystem):
        self.events = event_system
        self.is_locked = True
        self.current_user = None
        self.clipboard_content = None
        self.clipboard_timer_id = None
        self.last_activity_time = None
        self.inactivity_seconds = 0
        self._setup_listeners()

    def _setup_listeners(self):
        self.events.subscribe(Events.USER_LOGGED_IN, self._on_login)
        self.events.subscribe(Events.USER_LOGGED_OUT, self._on_logout)

    def _on_login(self, data):
        user = data if isinstance(data, str) else "Unknown"
        self.login(user)

    def _on_logout(self, data):
        self.logout()

    def login(self, username):
        print(f"[STATE] Пользователь вошел: {username}")
        self.is_locked = False
        self.current_user = username
        self.reset_activity()

    def logout(self):
        print("[STATE] Сессия завершена (logout)")
        self.is_locked = True
        self.current_user = None
        self.clipboard_content = None
        self.inactivity_seconds = 0

    def reset_activity(self):
        import time
        self.last_activity_time = time.time()
        self.inactivity_seconds = 0
