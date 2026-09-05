from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.core.database import Base

class LaboratorioReferencia(Base):
    __tablename__ = "laboratorios_referencia"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), unique=True, index=True, nullable=False)
    contacto = Column(String(150), nullable=True)
    telefono = Column(String(100), nullable=True)
    email = Column(String(150), nullable=True)
    direccion = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TipoInsumoCatalogo(Base):
    __tablename__ = "tipos_insumo_catalogo"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(50), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    color = Column(String(50), default="brand")
    base_calculo_sugerida = Column(String(20), default="test")
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
