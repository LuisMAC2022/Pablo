import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "cambia_esto_por_una_clave_secreta_larga"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas


def verificar_password(password_plano: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password_plano.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def hashear_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def crear_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None