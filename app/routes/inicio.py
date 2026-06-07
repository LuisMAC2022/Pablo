from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies import get_usuario_actual


router = APIRouter()


@router.get("/")
async def raiz():
    return RedirectResponse(url="/inicio", status_code=302)


@router.get("/inicio", response_class=HTMLResponse)
async def inicio(request: Request, usuario: dict = Depends(get_usuario_actual)):
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="inicio.html",
        context={
            "usuario": usuario,
        },
    )
