from typing import Optional


ROLES_SOLICITUDES = {"biologo", "admin", "desarrollador"}
ROLES_VISITANTES = {"seguridad", "admin", "desarrollador"}


def usuario_tiene_rol(usuario: Optional[dict], roles_permitidos: set[str]) -> bool:
    return bool(usuario and usuario.get("rol") in roles_permitidos)


ROLES_EDITAN_DATOS_SOLICITANTE = {"admin", "desarrollador"}


def puede_editar_datos_solicitante(usuario: Optional[dict]) -> bool:
    return bool(usuario and usuario.get("rol") in ROLES_EDITAN_DATOS_SOLICITANTE)
