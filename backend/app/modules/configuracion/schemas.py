from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# --- Laboratorios de Referencia ---
class LaboratorioReferenciaBase(BaseModel):
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool = True
    notas: Optional[str] = None

class LaboratorioReferenciaCreate(LaboratorioReferenciaBase):
    pass

class LaboratorioReferenciaUpdate(BaseModel):
    nombre: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None
    notas: Optional[str] = None

class LaboratorioReferenciaOut(LaboratorioReferenciaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Tipos de Insumo (Catálogo) ---
class TipoInsumoCatalogoBase(BaseModel):
    clave: str
    nombre: str
    descripcion: Optional[str] = None
    color: Optional[str] = "brand"
    base_calculo_sugerida: Optional[str] = "test"
    orden: Optional[int] = 0
    activo: bool = True

class TipoInsumoCatalogoCreate(TipoInsumoCatalogoBase):
    pass

class TipoInsumoCatalogoUpdate(BaseModel):
    clave: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    color: Optional[str] = None
    base_calculo_sugerida: Optional[str] = None
    orden: Optional[int] = None
    activo: Optional[bool] = None

class TipoInsumoCatalogoOut(TipoInsumoCatalogoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
