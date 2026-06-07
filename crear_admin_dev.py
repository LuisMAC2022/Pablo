from app.database import SessionLocal
from app.models import Usuario
from app.auth import hashear_password

def crear_usuarios_restantes():
    db = SessionLocal()
    
    usuarios = [
        Usuario(
            nombre="Administrador",
            email="admin@pabellon.mx",
            password_hash=hashear_password("admin123#PASS"),
            rol="admin"
        ),
        Usuario(
            nombre="Desarrollador",
            email="dev@pabellon.mx",
            password_hash=hashear_password("dev123#PASS"),
            rol="desarrollador"
        ),
    ]

    for usuario in usuarios:
        db.add(usuario)
    
    db.commit()
    db.close()
    print("Usuarios creados correctamente")

if __name__ == "__main__":
    crear_usuarios_restantes()
