from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class RegistroProduccionMensual(Base):
    __tablename__ = "registros_produccion_mensual"

    id = Column(Integer, primary_key=True, index=True)
    periodo_mes = Column(Integer, nullable=False) # 1 a 12
    periodo_anio = Column(Integer, nullable=False) # Ej: 2024, 2025
    
    determinacion_id = Column(Integer, ForeignKey("determinaciones.id", ondelete="CASCADE"), nullable=False)
    cantidad_estudios_realizados = Column(Integer, default=0, nullable=False)
    
    costo_unitario_historico_ars = Column(Numeric(14, 4), default=0.0)
    costo_total_mes_ars = Column(Numeric(14, 4), default=0.0)
    
    fuente = Column(String(50), default="manual") # 'manual', 'n8n_webhook', 'lis_import'
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    determinacion = relationship("Determinacion")

class RegistroComprasMensual(Base):
    __tablename__ = "registros_compras_mensual"

    id = Column(Integer, primary_key=True, index=True)
    periodo_mes = Column(Integer, nullable=False)
    periodo_anio = Column(Integer, nullable=False)
    insumo_id = Column(Integer, ForeignKey("insumos.id", ondelete="CASCADE"), nullable=False)
    
    cantidad_comprada = Column(Numeric(12, 4), default=0.0, nullable=False)
    monto_total_ars = Column(Numeric(14, 4), default=0.0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    insumo = relationship("Insumo")
