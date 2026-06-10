import json
import os
import sys
from pathlib import Path

from app.database import SessionLocal
from app.models import Usuario
from app.auth import hashear_password


ROL_USUARIO = "biologo"

# Para desarrollo usa "biologo123".
# En producción, define PASSWORD_TEMPORAL_BIOLOGOS en .env o en variables de entorno.
PASSWORD_TEMPORAL = os.getenv("PASSWORD_TEMPORAL_BIOLOGOS", "biologo123")


def cargar_registros(ruta_json: Path):
    with ruta_json.open("r", encoding="utf-8") as archivo:
        data = json.load(archivo)

    if isinstance(data, dict) and "registros" in data:
        return data["registros"]

    if isinstance(data, list):
        return data

    raise ValueError("El JSON debe contener una lista o un objeto con la clave 'registros'.")


def construir_nombre_completo(registro: dict) -> str:
    nombre = (registro.get("nombre") or "").strip()
    apellidos = (registro.get("apellidos") or "").strip()

    nombre_completo = f"{nombre} {apellidos}".strip()

    if not nombre_completo:
        raise ValueError("Registro sin nombre válido.")

    return nombre_completo


def crear_usuarios(ruta_json: str = "directorio_personal.json"):
    db = SessionLocal()

    try:
        registros = cargar_registros(Path(ruta_json))

        emails_existentes = {
            email for (email,) in db.query(Usuario.email).all()
        }

        emails_vistos = set()
        usuarios_creados = 0
        usuarios_omitidos = 0

        for registro in registros:
            email = (registro.get("email") or "").strip().lower()

            if not email:
                usuarios_omitidos += 1
                continue

            if email in emails_existentes or email in emails_vistos:
                usuarios_omitidos += 1
                continue

            nombre_completo = construir_nombre_completo(registro)

            usuario = Usuario(
                nombre=nombre_completo,
                email=email,
                password_hash=hashear_password(PASSWORD_TEMPORAL),
                rol=ROL_USUARIO,
            )

            db.add(usuario)
            emails_vistos.add(email)
            usuarios_creados += 1

        db.commit()

        print(f"Usuarios creados correctamente: {usuarios_creados}")
        print(f"Usuarios omitidos: {usuarios_omitidos}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "directorio_personal.json"
    crear_usuarios(ruta)