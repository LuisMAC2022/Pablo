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
	telefono = Column(String(30), nullable=False)
	responsable_area_solicitante = Column(String(100), nullable=True)
	area_solicitante = Column(String(100), nullable=False)
	infraestructura = Column(ARRAY(String), nullable=True)
	equipo_parque_vehicular = Column(ARRAY(String), nullable=True)
	seguridad = Column(ARRAY(String), nullable=True)
	transporte = Column(ARRAY(String), nullable=True)
	diversos_limpieza = Column(ARRAY(String), nullable=True)
	prestamo_de = Column(ARRAY(String), nullable=True)
	correspondencia_paqueteria = Column(ARRAY(String), nullable=True)
	reproduccion_engargolado = Column(ARRAY(String), nullable=True)
	descripcion_servicio = Column(Text, nullable=False)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    rol = Column(String(20), nullable=False)  # admin, biologo, desarrollador, seguridad