from app.auth import hashear_password
from app.config import get_settings
from app.database import SessionLocal
from app.models import Usuario


NOMBRE_BIOLOGO_PRUEBA = "Biólogo de Prueba"
EMAIL_BIOLOGO_PRUEBA = "biologo.prueba@pabellon.mx"
ROL_BIOLOGO = "biologo"


def crear_biologo_prueba():
    """Crea un único usuario biólogo de prueba si no existe."""
    db = SessionLocal()

    try:
        email = EMAIL_BIOLOGO_PRUEBA.lower()
        usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()

        if usuario_existente:
            print(f"El usuario biólogo de prueba ya existe: {email}")
            return usuario_existente

        password_temporal = get_settings().password_temporal_biologos.get_secret_value()
        usuario = Usuario(
            nombre=NOMBRE_BIOLOGO_PRUEBA,
            email=email,
            password_hash=hashear_password(password_temporal),
            rol=ROL_BIOLOGO,
        )

        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        print("Usuario biólogo de prueba creado correctamente")
        print(f"Email: {email}")
        print("Contraseña: usa el valor de PASSWORD_TEMPORAL_BIOLOGOS")
        return usuario

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    crear_biologo_prueba()
