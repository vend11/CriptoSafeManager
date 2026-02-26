def derive_key(self, password: str, salt: bytes) -> bytes:
        return password.encode().ljust(32, b'\0')[:32]

def store_key(self): pass

def load_key(self): pass
