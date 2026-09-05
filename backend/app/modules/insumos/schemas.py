from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from app.modules.insumos.models import TipoInsumo, BaseCalculoInsumo, Moneda

class InsumoBase(BaseModel):
    codigo: Optional[str] = None
    nombre: str
    marca_proveedor: Optional[str] = None
    tipo: str = "reactivo" # Clave del tipo según catálogo
    base_calculo: BaseCalculoInsumo = BaseCalculoInsumo.TEST
    presentacion: Optional[str] = None
    cantidad_por_presentacion: Decimal = Field(default=Decimal("1.0"), gt=Decimal("0.0"))
    unidad_medida: str = "test"
    costo_presentacion: Decimal = Field(gt=Decimal("0.0"))
    moneda: Moneda = Moneda.USD
    tipo_cambio_al_costear: Decimal = Field(default=Decimal("1200.0"), gt=Decimal("0.0"))
    unidades_compradas_periodo: Decimal = Field(default=Decimal("1.0"), gt=Decimal("0.0"))
    determinaciones_periodo: Decimal = Field(default=Decimal("1.0"), gt=Decimal("0.0"))
    merma_estimada_porcentaje: Decimal = Field(default=Decimal("0.0"), ge=Decimal("0.0"), le=Decimal("100.0"))
    activo: bool = True
    notas: Optional[str] = None

class InsumoCreate(InsumoBase):
    pass

class InsumoUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    marca_proveedor: Optional[str] = None
    tipo: Optional[str] = None
    base_calculo: Optional[BaseCalculoInsumo] = None
    presentacion: Optional[str] = None
    cantidad_por_presentacion: Optional[Decimal] = None
    unidad_medida: Optional[str] = None
    costo_presentacion: Optional[Decimal] = None
    moneda: Optional[Moneda] = None
    tipo_cambio_al_costear: Optional[Decimal] = None
    unidades_compradas_periodo: Optional[Decimal] = None
    determinaciones_periodo: Optional[Decimal] = None
    merma_estimada_porcentaje: Optional[Decimal] = None
    activo: Optional[bool] = None
    notas: Optional[str] = None

class InsumoOut(InsumoBase):
    id: int
    costo_por_determinacion_usd: Decimal = Field(default=Decimal("0.0"))
    costo_unitario_ars: Decimal = Field(default=Decimal("0.0"))
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
