class AppConfig:
    DB_NAME = "cryptosafe.db"
    KDF_ALGORITHM = "PBKDF2HMAC"
    KDF_LENGTH = 32
    KDF_ITERATIONS = 480000
    SALT_SIZE = 16
    NONCE_SIZE = 12
    ENCODING = "utf-8"
