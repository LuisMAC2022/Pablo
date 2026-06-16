from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import auth, inicio, solicitudes, visitantes


settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)
templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(inicio.router)
app.include_router(auth.router)
app.include_router(solicitudes.router)
app.include_router(visitantes.router)
