from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class DeterminacionInsumo(Base):
    __tablename__ = "determinacion_insumos"

    id = Column(Integer, primary_key=True, index=True)
    determinacion_id = Column(Integer, ForeignKey("determinaciones.id", ondelete="CASCADE"), nullable=False)
    insumo_id = Column(Integer, ForeignKey("insumos.id", ondelete="RESTRICT"), nullable=False)

    # Cantidad que consume este estudio de la unidad del insumo (ej: 1 test, o 0.05 ml, o 1 tubo)
    cantidad_requerida = Column(Numeric(12, 4), default=1.0, nullable=False)

    # Relaciones
    determinacion = relationship("Determinacion", back_populates="insumos_asociados")
    insumo = relationship("Insumo")

class Determinacion(Base):
    __tablename__ = "determinaciones"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=True) # Código interno o nomenclador
    codigo_nomenclador = Column(String(50), nullable=True) # Nomenclador bioquímico nacional / provincial
    nombre = Column(String(200), nullable=False, index=True)
    seccion = Column(String(100), nullable=False) # Quimica, Hematologia, etc.

    # Asignación de equipo por defecto
    equipo_id = Column(Integer, ForeignKey("equipos.id", ondelete="SET NULL"), nullable=True)

    # Parámetros operativos y técnicos
    tiempo_proceso_minutos = Column(Numeric(8, 2), default=0.0) # Tiempo de operador/técnico
    tasa_repeticion_porcentaje = Column(Numeric(5, 2), default=0.0) # Factor de repetición (ej: 5% -> 1.05)

    # Arancel sugerido / precio de venta para cálculo de margen
    arancel_referencia_ars = Column(Numeric(14, 4), default=0.0)
    arancel_referencia_usd = Column(Numeric(14, 4), default=0.0)

    # Costos calculados cacheados / snapshot (en ARS y USD)
    costo_reactivos_ars = Column(Numeric(14, 4), default=0.0)
    costo_reactivos_usd = Column(Numeric(14, 6), default=0.0)
    costo_equipo_ars = Column(Numeric(14, 4), default=0.0)
    costo_equipo_usd = Column(Numeric(14, 6), default=0.0)
    costo_repeticion_ars = Column(Numeric(14, 4), default=0.0)
    costo_mano_obra_ars = Column(Numeric(14, 4), default=0.0)
    costo_mano_obra_usd = Column(Numeric(14, 6), default=0.0)
    costo_unitario_total_ars = Column(Numeric(14, 4), default=0.0)
    costo_unitario_total_usd = Column(Numeric(14, 6), default=0.0)

    # Metadatos
    activo = Column(Boolean, default=True)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    equipo = relationship("Equipo", back_populates="determinaciones")
    insumos_asociados = relationship("DeterminacionInsumo", back_populates="determinacion", cascade="all, delete-orphan")
