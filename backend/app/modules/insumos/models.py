from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, Enum
import enum
from app.core.database import Base

class TipoInsumo(str, enum.Enum):
    REACTIVO = "reactivo"
    CALIBRADOR = "calibrador"
    CONTROL = "control"
    SOLUCION_LAVADO = "solucion_lavado"
    DESCARTABLE_EXTRACCION = "descartable_extraccion"
    DESCARTABLE_EQUIPO = "descartable_equipo"
    OTRO = "otro"

class BaseCalculoInsumo(str, enum.Enum):
    TEST = "test"           # Costeo en base a determinaciones / tests entregados
    PACIENTE = "paciente"   # Costeo en base a pacientes atendidos / extracciones

class Moneda(str, enum.Enum):
    ARS = "ARS"
    USD = "USD"

class Insumo(Base):
    __tablename__ = "insumos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=True)
    nombre = Column(String(200), nullable=False, index=True)
    marca_proveedor = Column(String(150), nullable=True)
    tipo = Column(String(50), default="reactivo", nullable=False) # Clave del tipo según tipos_insumo_catalogo
    base_calculo = Column(Enum(BaseCalculoInsumo), default=BaseCalculoInsumo.TEST, nullable=False)

    # Presentación y rendimiento de compra
    presentacion = Column(String(100), nullable=True) # Ej: "Kit x 100 tests", "Frasco 500ml", "Caja x 100 tubos"
    cantidad_por_presentacion = Column(Numeric(14, 4), default=1.0) # Cantidad unitaria/empaque
    unidad_medida = Column(String(50), default="test") # test, paciente, unidad, ml, frasco

    # Costos y Moneda de Compra
    costo_presentacion = Column(Numeric(14, 4), nullable=False) # Precio de compra por unidad/frasco
    moneda = Column(Enum(Moneda), default=Moneda.USD, nullable=False)
    tipo_cambio_al_costear = Column(Numeric(10, 4), default=1200.0) # Si fue en USD, TC usado

    # Parámetros del Período Real de Producción (Fórmula exacta por lote)
    unidades_compradas_periodo = Column(Numeric(14, 4), default=1.0) # Ej: 4 reactivos, 1 calibrador, 100 tubos
    determinaciones_periodo = Column(Numeric(14, 4), default=1.0) # Ej: 31445 tests (si base_calculo=test) o 1500 pacientes (si base_calculo=paciente)

    # Costos Unitarios Resultantes (por test o por paciente)
    costo_por_determinacion_usd = Column(Numeric(14, 6), default=0.0) # (costo * unidades) / determinaciones_o_pacientes
    costo_unitario_ars = Column(Numeric(14, 6), nullable=False) # costo en ARS resultante

    # Trazabilidad y mermas adicionales
    merma_estimada_porcentaje = Column(Numeric(5, 2), default=0.0)

    activo = Column(Boolean, default=True)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
