from typing import Optional, List, Any
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

from app.modules.equipos.models import MonedaEquipo

class ConsumibleMantenimiento(BaseModel):
    nombre: str
    costo_mensual: Decimal = Field(default=Decimal("0.0"))
    descripcion: Optional[str] = None

class EquipoBase(BaseModel):
    nombre: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    seccion: str
    moneda: MonedaEquipo = MonedaEquipo.USD
    tipo_cambio_al_costear: Decimal = Field(default=Decimal("1200.0"), gt=Decimal("0.0"))
    costo_alquiler_mensual: Decimal = Field(default=Decimal("0.0"))
    costo_mantenimiento_mensual: Decimal = Field(default=Decimal("0.0"))
    costo_amortizacion_mensual: Decimal = Field(default=Decimal("0.0"))
    costo_calibracion_controles_mensual: Decimal = Field(default=Decimal("0.0"))
    volumen_mensual_estimado: int = Field(default=1000, gt=0)
    consumibles_mantenimiento: List[ConsumibleMantenimiento] = []
    activo: bool = True
    notas: Optional[str] = None

class EquipoCreate(EquipoBase):
    pass

class EquipoUpdate(BaseModel):
    nombre: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    seccion: Optional[str] = None
    moneda: Optional[MonedaEquipo] = None
    tipo_cambio_al_costear: Optional[Decimal] = None
    costo_alquiler_mensual: Optional[Decimal] = None
    costo_mantenimiento_mensual: Optional[Decimal] = None
    costo_amortizacion_mensual: Optional[Decimal] = None
    costo_calibracion_controles_mensual: Optional[Decimal] = None
    volumen_mensual_estimado: Optional[int] = None
    consumibles_mantenimiento: Optional[List[ConsumibleMantenimiento]] = None
    activo: Optional[bool] = None
    notas: Optional[str] = None

class EquipoOut(EquipoBase):
    id: int
    costo_total_mensual: Decimal = Field(default=Decimal("0.0"))
    costo_total_mensual_usd: Decimal = Field(default=Decimal("0.0"))
    costo_unitario_por_test: Decimal = Field(default=Decimal("0.0"))
    costo_unitario_por_test_usd: Decimal = Field(default=Decimal("0.0"))
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
