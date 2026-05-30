from sqlalchemy import Column, Integer, String, Text, Date, ARRAY
from sqlalchemy.orm import declarative_base
from datetime import date

Base = declarative_base()

class Solicitud(Base):

	__tablename__ = "solicitudes"

	id = Column(Integer, primary_key=True, autoincrement=True)
	folio = Column(String(10), unique=True, nullable=False)
	fecha = Column(Date, default=date.today, nullable=False)
	nombre_usuario = Column(String(100), nullable=False)
	telefono = Column(String(20), nullable=False)
	area_solicitante = Column(String(100), nullable=False)
	infraestructura = Column(ARRAY(String), nullable=True)
	equipo_parque_vehicular = Column(ARRAY(String), nullable=True)
	descripcion_servicio = Column(Text, nullable=False)
