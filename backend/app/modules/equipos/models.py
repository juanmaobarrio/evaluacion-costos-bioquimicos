from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class MonedaEquipo(str, enum.Enum):
    ARS = "ARS"
    USD = "USD"

class Equipo(Base):
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), unique=True, index=True, nullable=False)
    marca = Column(String(100), nullable=True)
    modelo = Column(String(100), nullable=True)
    seccion = Column(String(100), nullable=False) # ej: Quimica Clinica, Hematologia, Inmunologia

    # Moneda y Tipo de Cambio
    moneda = Column(Enum(MonedaEquipo), default=MonedaEquipo.USD, nullable=False)
    tipo_cambio_al_costear = Column(Numeric(10, 4), default=1200.0)

    # Costos fijos mensuales del equipo (en la moneda seleccionada)
    costo_alquiler_mensual = Column(Numeric(14, 4), default=0.0)
    costo_mantenimiento_mensual = Column(Numeric(14, 4), default=0.0)
    costo_amortizacion_mensual = Column(Numeric(14, 4), default=0.0)
    costo_calibracion_controles_mensual = Column(Numeric(14, 4), default=0.0)

    # Volumen promedio mensual estimado procesado por este equipo
    volumen_mensual_estimado = Column(Integer, default=1000)

    # Consumibles fijos de mantenimiento (opcional)
    consumibles_mantenimiento = Column(JSON, default=list)

    activo = Column(Boolean, default=True)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    activo = Column(Boolean, default=True)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    determinaciones = relationship("Determinacion", back_populates="equipo")
