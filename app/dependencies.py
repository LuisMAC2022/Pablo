from typing import Optional

from fastapi import Cookie

from app.auth import verificar_token


def get_usuario_actual(token: Optional[str] = Cookie(None)):
    if not token:
        return None
    return verificar_token(token)
