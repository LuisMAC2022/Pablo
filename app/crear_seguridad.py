from app.database import SessionLocal
from app.models import Usuario
from app.auth import hashear_password

def crear_usuario_seguridad():
    db = SessionLocal()
    
    usuario = Usuario(
        nombre="Seguridad",
        email="seguridad@pabellon.mx",
        password_hash=hashear_password("seguridad123"),
        rol="seguridad"
    )
    db.add(usuario)
    db.commit()
    db.close()
    print("Usuario seguridad creado correctamente")

if __name__ == "__main__":
    crear_usuario_seguridad()