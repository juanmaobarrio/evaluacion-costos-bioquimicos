from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from app.modules.insumos.schemas import InsumoOut
from app.modules.equipos.schemas import EquipoOut
from app.modules.configuracion.schemas import LaboratorioReferenciaOut

class DeterminacionInsumoCreate(BaseModel):
    insumo_id: int
    cantidad_requerida: Decimal = Field(default=Decimal("1.0"), gt=Decimal("0.0"))

class DeterminacionInsumoOut(BaseModel):
    id: int
    insumo_id: int
    cantidad_requerida: Decimal
    insumo: Optional[InsumoOut] = None
    costo_subtotal_ars: Decimal = Field(default=Decimal("0.0"))
    costo_subtotal_usd: Decimal = Field(default=Decimal("0.0"))

    class Config:
        from_attributes = True

class DeterminacionBase(BaseModel):
    codigo: Optional[str] = None
    codigo_nomenclador: Optional[str] = None
    nombre: str
    seccion: str
    equipo_id: Optional[int] = None
    tiempo_proceso_minutos: Decimal = Field(default=Decimal("0.0"), ge=Decimal("0.0"))
    tasa_repeticion_porcentaje: Decimal = Field(default=Decimal("0.0"), ge=Decimal("0.0"), le=Decimal("100.0"))
    arancel_referencia_ars: Decimal = Field(default=Decimal("0.0"), ge=Decimal("0.0"))
    arancel_referencia_usd: Decimal = Field(default=Decimal("0.0"), ge=Decimal("0.0"))
    costo_referencia_ars: Decimal = Field(default=Decimal("0.0"), ge=Decimal("0.0"))
    costo_referencia_usd: Decimal = Field(default=Decimal("0.0"), ge=Decimal("0.0"))
    laboratorio_referencia_id: Optional[int] = None
    activo: bool = True
    notas: Optional[str] = None

class DeterminacionCreate(DeterminacionBase):
    insumos: List[DeterminacionInsumoCreate] = []

class DeterminacionUpdate(BaseModel):
    codigo: Optional[str] = None
    codigo_nomenclador: Optional[str] = None
    nombre: Optional[str] = None
    seccion: Optional[str] = None
    equipo_id: Optional[int] = None
    tiempo_proceso_minutos: Optional[Decimal] = None
    tasa_repeticion_porcentaje: Optional[Decimal] = None
    arancel_referencia_ars: Optional[Decimal] = None
    arancel_referencia_usd: Optional[Decimal] = None
    costo_referencia_ars: Optional[Decimal] = None
    costo_referencia_usd: Optional[Decimal] = None
    laboratorio_referencia_id: Optional[int] = None
    activo: Optional[bool] = None
    notas: Optional[str] = None
    insumos: Optional[List[DeterminacionInsumoCreate]] = None

class DeterminacionOut(DeterminacionBase):
    id: int
    costo_reactivos_ars: Decimal = Field(default=Decimal("0.0"))
    costo_reactivos_usd: Decimal = Field(default=Decimal("0.0"))
    costo_equipo_ars: Decimal = Field(default=Decimal("0.0"))
    costo_equipo_usd: Decimal = Field(default=Decimal("0.0"))
    costo_repeticion_ars: Decimal = Field(default=Decimal("0.0"))
    costo_mano_obra_ars: Decimal = Field(default=Decimal("0.0"))
    costo_mano_obra_usd: Decimal = Field(default=Decimal("0.0"))
    costo_unitario_total_ars: Decimal = Field(default=Decimal("0.0"))
    costo_unitario_total_usd: Decimal = Field(default=Decimal("0.0"))
    margen_estimado_porcentaje: Optional[Decimal] = Field(default=Decimal("0.0"))
    margen_bruto_ars: Optional[Decimal] = Field(default=Decimal("0.0"))
    margen_bruto_usd: Optional[Decimal] = Field(default=Decimal("0.0"))
    # Comparativa de costo interno vs laboratorio externo de referencia
    diferencia_referencia_ars: Optional[Decimal] = Field(default=Decimal("0.0"))
    diferencia_referencia_porcentaje: Optional[Decimal] = Field(default=Decimal("0.0"))
    equipo: Optional[EquipoOut] = None
    laboratorio_referencia: Optional[LaboratorioReferenciaOut] = None
    insumos_asociados: List[DeterminacionInsumoOut] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
