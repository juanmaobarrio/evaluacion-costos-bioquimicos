from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from app.modules.insumos.schemas import InsumoOut
from app.modules.determinaciones.schemas import DeterminacionOut

# --- Secciones del Laboratorio ---
class SeccionLaboratorioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    color: Optional[str] = "emerald"
    activo: bool = True

class SeccionLaboratorioCreate(SeccionLaboratorioBase):
    pass

class SeccionLaboratorioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    color: Optional[str] = None
    activo: Optional[bool] = None

class SeccionLaboratorioOut(SeccionLaboratorioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Gastos Fijos ---
class GastoFijoBase(BaseModel):
    concepto: str
    categoria: str = "Servicios"
    monto_mensual: Decimal = Field(gt=Decimal("0.0"))
    activo: bool = True
    notas: Optional[str] = None

class GastoFijoCreate(GastoFijoBase):
    pass

class GastoFijoUpdate(BaseModel):
    concepto: Optional[str] = None
    categoria: Optional[str] = None
    monto_mensual: Optional[Decimal] = None
    activo: Optional[bool] = None
    notas: Optional[str] = None

class GastoFijoOut(GastoFijoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Parámetros de Laboratorio ---
class ParametroLaboratorioBase(BaseModel):
    clave: str
    valor_numerico: Optional[Decimal] = None
    valor_texto: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: str = "General"

class ParametroLaboratorioCreate(ParametroLaboratorioBase):
    pass

class ParametroLaboratorioUpdate(BaseModel):
    valor_numerico: Optional[Decimal] = None
    valor_texto: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None

class ParametroLaboratorioOut(ParametroLaboratorioBase):
    id: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Materiales Extracción ---
class MaterialExtraccionItemCreate(BaseModel):
    insumo_id: int
    cantidad: Decimal = Field(default=Decimal("1.0"), gt=Decimal("0.0"))
    es_obligatorio: bool = True

class MaterialExtraccionItemOut(BaseModel):
    id: int
    insumo_id: int
    cantidad: Decimal
    es_obligatorio: bool
    insumo: Optional[InsumoOut] = None
    costo_subtotal_ars: Decimal = Field(default=Decimal("0.0"))

    class Config:
        from_attributes = True

# --- Protocolos ---
class ProtocoloEstudioCreate(BaseModel):
    determinacion_id: int

class ProtocoloEstudioOut(BaseModel):
    id: int
    determinacion_id: int
    determinacion: Optional[DeterminacionOut] = None

    class Config:
        from_attributes = True

class ProtocoloBase(BaseModel):
    nombre: str
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    arancel_sugerido_ars: Decimal = Field(default=Decimal("0.0"), ge=Decimal("0.0"))
    activo: bool = True

class ProtocoloCreate(ProtocoloBase):
    determinacion_ids: List[int] = []

class ProtocoloUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    arancel_sugerido_ars: Optional[Decimal] = None
    activo: Optional[bool] = None
    determinacion_ids: Optional[List[int]] = None

class ProtocoloOut(ProtocoloBase):
    id: int
    costo_determinaciones_ars: Decimal = Field(default=Decimal("0.0"))
    costo_extraccion_descartables_ars: Decimal = Field(default=Decimal("0.0"))
    costo_overhead_fijo_ars: Decimal = Field(default=Decimal("0.0"))
    costo_total_protocolo_ars: Decimal = Field(default=Decimal("0.0"))
    margen_bruto_ars: Decimal = Field(default=Decimal("0.0"))
    margen_estimado_porcentaje: Decimal = Field(default=Decimal("0.0"))
    estudios: List[ProtocoloEstudioOut] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
