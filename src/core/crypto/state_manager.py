class StateManager:
    def __init__(self):
        self.is_locked = True
        self.clipboard_data = None
        self.inactivity_timer = 0
