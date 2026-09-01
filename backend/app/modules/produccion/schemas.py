from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from app.modules.determinaciones.schemas import DeterminacionOut
from app.modules.insumos.schemas import InsumoOut

class ProduccionItemIn(BaseModel):
    determinacion_codigo_o_id: str | int
    cantidad_estudios: int = Field(ge=0)

class ProduccionBatchImport(BaseModel):
    periodo_mes: int = Field(ge=1, le=12)
    periodo_anio: int = Field(ge=2000, le=2100)
    fuente: str = "n8n_webhook"
    items: List[ProduccionItemIn]

class ProduccionRegistroCreate(BaseModel):
    periodo_mes: int = Field(ge=1, le=12)
    periodo_anio: int = Field(ge=2000, le=2100)
    determinacion_id: int
    cantidad_estudios_realizados: int = Field(ge=0)
    fuente: str = "manual"
    notas: Optional[str] = None

class ProduccionRegistroOut(BaseModel):
    id: int
    periodo_mes: int
    periodo_anio: int
    determinacion_id: int
    cantidad_estudios_realizados: int
    costo_unitario_historico_ars: Decimal
    costo_total_mes_ars: Decimal
    fuente: str
    notas: Optional[str] = None
    created_at: datetime
    determinacion: Optional[DeterminacionOut] = None

    class Config:
        from_attributes = True

# Conciliación y Comparativa
class ConciliacionItemOut(BaseModel):
    insumo_id: int
    insumo_nombre: str
    consumo_teorico_unidades: Decimal
    consumo_teorico_ars: Decimal
    compras_reales_unidades: Decimal
    compras_reales_ars: Decimal
    desvio_unidades: Decimal
    desvio_ars: Decimal
    desvio_porcentaje: Decimal
    alerta: bool
