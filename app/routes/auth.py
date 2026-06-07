from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth import crear_token, verificar_password
from app.database import get_db
from app.models import Usuario


router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def mostrar_login(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None,
        },
    )


@router.post("/login")
async def recibir_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario or not verificar_password(password, usuario.password_hash):
        templates = request.app.state.templates
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Correo o contraseña incorrectos.",
            },
            status_code=400,
        )

    token = crear_token(
        {
            "sub": usuario.email,
            "rol": usuario.rol,
            "nombre": usuario.nombre,
        }
    )

    response = RedirectResponse(url="/inicio", status_code=302)
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("token")
    return response
