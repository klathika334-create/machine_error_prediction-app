import os

SECRET_KEY = os.getenv("APP_SECRET_KEY", "change_this_in_production")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_in_production")
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_EXPIRES_SECONDS", "3600"))
BCRYPT_LOG_ROUNDS = int(os.getenv("BCRYPT_LOG_ROUNDS", "12"))
