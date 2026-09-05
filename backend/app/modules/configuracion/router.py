from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.service import get_current_user, require_role
from app.modules.auth.models import UserRole
from app.modules.configuracion.schemas import (
    LaboratorioReferenciaCreate, LaboratorioReferenciaUpdate, LaboratorioReferenciaOut,
    TipoInsumoCatalogoCreate, TipoInsumoCatalogoUpdate, TipoInsumoCatalogoOut
)
from app.modules.configuracion.service import (
    LaboratoriosReferenciaService, TiposInsumoService
)

router = APIRouter(tags=["Configuración Global del Sistema"])

# =====================================================================
# LABORATORIOS DE REFERENCIA / DERIVACIÓN EXTERNA
# =====================================================================
@router.get("/laboratorios-referencia", response_model=List[LaboratorioReferenciaOut])
async def list_laboratorios_referencia(
    activo_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await LaboratoriosReferenciaService.get_all(db, activo_only=activo_only)

@router.get("/laboratorios-referencia/{lab_id}", response_model=LaboratorioReferenciaOut)
async def get_laboratorio_referencia(
    lab_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    lab = await LaboratoriosReferenciaService.get_by_id(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Laboratorio de referencia no encontrado")
    return lab

@router.post("/laboratorios-referencia", response_model=LaboratorioReferenciaOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def create_laboratorio_referencia(
    lab_in: LaboratorioReferenciaCreate,
    db: AsyncSession = Depends(get_db)
):
    return await LaboratoriosReferenciaService.create(db, lab_in)

@router.put("/laboratorios-referencia/{lab_id}", response_model=LaboratorioReferenciaOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def update_laboratorio_referencia(
    lab_id: int,
    lab_in: LaboratorioReferenciaUpdate,
    db: AsyncSession = Depends(get_db)
):
    lab = await LaboratoriosReferenciaService.update(db, lab_id, lab_in)
    if not lab:
        raise HTTPException(status_code=404, detail="Laboratorio de referencia no encontrado")
    return lab

@router.delete("/laboratorios-referencia/{lab_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def delete_laboratorio_referencia(
    lab_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await LaboratoriosReferenciaService.delete(db, lab_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Laboratorio de referencia no encontrado")
    return {"message": "Laboratorio de referencia eliminado con éxito"}

# =====================================================================
# TIPOS DE INSUMO (CATÁLOGO DINÁMICO)
# =====================================================================
@router.get("/tipos-insumo", response_model=List[TipoInsumoCatalogoOut])
async def list_tipos_insumo(
    activo_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await TiposInsumoService.get_all(db, activo_only=activo_only)

@router.get("/tipos-insumo/{tipo_id}", response_model=TipoInsumoCatalogoOut)
async def get_tipo_insumo(
    tipo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    t = await TiposInsumoService.get_by_id(db, tipo_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tipo de insumo no encontrado")
    return t

@router.post("/tipos-insumo", response_model=TipoInsumoCatalogoOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def create_tipo_insumo(
    tipo_in: TipoInsumoCatalogoCreate,
    db: AsyncSession = Depends(get_db)
):
    return await TiposInsumoService.create(db, tipo_in)

@router.put("/tipos-insumo/{tipo_id}", response_model=TipoInsumoCatalogoOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def update_tipo_insumo(
    tipo_id: int,
    tipo_in: TipoInsumoCatalogoUpdate,
    db: AsyncSession = Depends(get_db)
):
    t = await TiposInsumoService.update(db, tipo_id, tipo_in)
    if not t:
        raise HTTPException(status_code=404, detail="Tipo de insumo no encontrado")
    return t

@router.delete("/tipos-insumo/{tipo_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def delete_tipo_insumo(
    tipo_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await TiposInsumoService.delete(db, tipo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tipo de insumo no encontrado")
    return {"message": "Tipo de insumo eliminado con éxito"}
