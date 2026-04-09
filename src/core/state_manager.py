import time
from src.core.events import EventSystem, Events

class StateManager:
    def __init__(self, event_system: EventSystem):
        self.events = event_system

        self.login_time = None
        self.last_activity_time = None
        self.failed_attempts = 0
        self.is_locked = True
        self.current_user = None
        self.inactivity_seconds = 0
        self._setup_listeners()

    def _setup_listeners(self):
        self.events.subscribe(Events.USER_LOGGED_IN, self._on_login)
        self.events.subscribe(Events.USER_LOGGED_OUT, self._on_logout)

    def _on_login(self, data):
        username = data if isinstance(data, str) else "Unknown"
        self.login(username)

    def _on_logout(self, data):
        self.logout()

    def login(self, username: str):
        self.is_locked = False
        self.current_user = username
        self.login_time = time.time()
        self.reset_activity()

    def logout(self):
        self.is_locked = True
        self.current_user = None
        self.login_time = None
        self.last_activity_time = None
        self.failed_attempts = 0
        self.inactivity_seconds = 0

    def reset_activity(self):
        self.last_activity_time = time.time()
        self.inactivity_seconds = 0

    def increment_failed_attempts(self) -> int:
        self.failed_attempts += 1
        return self.failed_attempts

    def get_session_duration(self) -> str:
        if not self.login_time:
            return "00:00:00"
        seconds = int(time.time() - self.login_time)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_session_info(self) -> dict:
        return {
            "login_time": self.login_time,
            "failed_attempts": self.failed_attempts,
            "is_locked": self.is_locked,
            "current_user": self.current_user,
        }
