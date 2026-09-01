from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class GastoFijoMensual(Base):
    __tablename__ = "gastos_fijos_mensuales"

    id = Column(Integer, primary_key=True, index=True)
    concepto = Column(String(200), nullable=False) # Alquiler Sede Central, Luz/Edenor, Sueldos Maestranza, etc.
    categoria = Column(String(100), default="Servicios") # Servicios, Sueldos, Alquileres, Software, Impuestos
    monto_mensual = Column(Numeric(14, 4), nullable=False)
    activo = Column(Boolean, default=True)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ParametroLaboratorio(Base):
    __tablename__ = "parametros_laboratorio"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(100), unique=True, index=True, nullable=False)
    valor_numerico = Column(Numeric(14, 4), nullable=True)
    valor_texto = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    categoria = Column(String(100), default="General") # ej: "Produccion", "ManoDeObra", "Moneda"
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MaterialExtraccionItem(Base):
    """Kit estándar o configurable de material descartable por extracción/paciente."""
    __tablename__ = "materiales_extraccion_items"

    id = Column(Integer, primary_key=True, index=True)
    insumo_id = Column(Integer, ForeignKey("insumos.id", ondelete="CASCADE"), nullable=False)
    cantidad = Column(Numeric(10, 4), default=1.0, nullable=False)
    es_obligatorio = Column(Boolean, default=True) # Siempre se computa por paciente
    
    insumo = relationship("Insumo")

class ProtocoloEstudio(Base):
    __tablename__ = "protocolo_estudios"

    id = Column(Integer, primary_key=True, index=True)
    protocolo_id = Column(Integer, ForeignKey("protocolos.id", ondelete="CASCADE"), nullable=False)
    determinacion_id = Column(Integer, ForeignKey("determinaciones.id", ondelete="CASCADE"), nullable=False)

    protocolo = relationship("Protocolo", back_populates="estudios")
    determinacion = relationship("Determinacion")

class Protocolo(Base):
    __tablename__ = "protocolos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True) # Ej: "Perfil Lipídico", "Chequeo Básico", "Rutina Quirúrgica"
    codigo = Column(String(50), unique=True, nullable=True)
    descripcion = Column(Text, nullable=True)
    
    # Costos calculados
    costo_determinaciones_ars = Column(Numeric(14, 4), default=0.0)
    costo_extraccion_descartables_ars = Column(Numeric(14, 4), default=0.0)
    costo_overhead_fijo_ars = Column(Numeric(14, 4), default=0.0)
    costo_total_protocolo_ars = Column(Numeric(14, 4), default=0.0)
    
    arancel_sugerido_ars = Column(Numeric(14, 4), default=0.0)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    estudios = relationship("ProtocoloEstudio", back_populates="protocolo", cascade="all, delete-orphan")
