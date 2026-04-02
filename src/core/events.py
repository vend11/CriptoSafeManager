import asyncio
from typing import Callable, Dict, List, Any

class EventSystem:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def publish(self, event_name: str, data: Any = None):
        callbacks = self._listeners.get(event_name, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.run(callback(data))
                else:
                    callback(data)
            except Exception as e:
                print(f"Event error [{event_name}]: {e}")

class Events:
    ENTRY_ADDED = "EntryAdded"
    ENTRY_UPDATED = "EntryUpdated"
    ENTRY_DELETED = "EntryDeleted"
    USER_LOGGED_IN = "UserLoggedIn"
    USER_LOGGED_OUT = "UserLoggedOut"
    CLIPBOARD_COPIED = "ClipboardCopied"
    CLIPBOARD_CLEARED = "ClipboardCleared"
