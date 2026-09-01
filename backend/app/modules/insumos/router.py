from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.service import get_current_user, require_role
from app.modules.auth.models import UserRole
from app.modules.insumos.models import TipoInsumo
from app.modules.insumos.schemas import InsumoCreate, InsumoUpdate, InsumoOut
from app.modules.insumos.service import InsumoService

router = APIRouter(prefix="/insumos", tags=["Insumos y Reactivos"])

@router.get("", response_model=List[InsumoOut])
async def list_insumos(
    tipo: Optional[TipoInsumo] = Query(None, description="Filtrar por tipo de insumo"),
    search: Optional[str] = Query(None, description="Buscar por nombre, código o marca"),
    activo_only: bool = Query(False, description="Solo insumos activos"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await InsumoService.get_all(db, tipo=tipo, search=search, activo_only=activo_only)

@router.get("/{insumo_id}", response_model=InsumoOut)
async def get_insumo(
    insumo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    insumo = await InsumoService.get_by_id(db, insumo_id)
    if not insumo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")
    return insumo

@router.post("", response_model=InsumoOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def create_insumo(
    insumo_in: InsumoCreate,
    db: AsyncSession = Depends(get_db)
):
    return await InsumoService.create(db, insumo_in)

@router.put("/{insumo_id}", response_model=InsumoOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def update_insumo(
    insumo_id: int,
    insumo_in: InsumoUpdate,
    db: AsyncSession = Depends(get_db)
):
    insumo = await InsumoService.update(db, insumo_id, insumo_in)
    if not insumo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")
    return insumo

@router.delete("/{insumo_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def delete_insumo(
    insumo_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await InsumoService.delete(db, insumo_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")
    return {"message": "Insumo eliminado correctamente"}
