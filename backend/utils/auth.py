from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext

SECRET_KEY = "secret-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600

# Заменили bcrypt → pbkdf2_sha256 (работает стабильно)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
    # except ExpiredSignatureError:
    #     return None
    # except InvalidTokenError:
    #     return None
