from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from app.routes import auth, inicio, solicitudes, visitantes


app = FastAPI()
app.state.templates = Jinja2Templates(directory="app/templates")

app.include_router(inicio.router)
app.include_router(auth.router)
app.include_router(solicitudes.router)
app.include_router(visitantes.router)
