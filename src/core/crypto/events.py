_listeners = {}

def subscribe(event_type, callback):
    if event_type not in _listeners: _listeners[event_type] = []
    _listeners[event_type].append(callback)

def emit(event_type, data=None):
    if event_type in _listeners:
        for cb in _listeners[event_type]: cb(data)
