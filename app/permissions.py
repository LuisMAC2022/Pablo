from typing import Optional


ROLES_SOLICITUDES = {"biologo", "admin", "desarrollador"}
ROLES_VISITANTES = {"seguridad", "admin", "desarrollador"}


def usuario_tiene_rol(usuario: Optional[dict], roles_permitidos: set[str]) -> bool:
    return bool(usuario and usuario.get("rol") in roles_permitidos)
