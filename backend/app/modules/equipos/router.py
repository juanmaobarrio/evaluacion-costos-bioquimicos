from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.service import get_current_user, require_role
from app.modules.auth.models import UserRole
from app.modules.equipos.schemas import EquipoCreate, EquipoUpdate, EquipoOut
from app.modules.equipos.service import EquipoService

router = APIRouter(prefix="/equipos", tags=["Equipos y Autoanalizadores"])

@router.get("", response_model=List[EquipoOut])
async def list_equipos(
    seccion: Optional[str] = Query(None, description="Filtrar por sección"),
    activo_only: bool = Query(False, description="Solo equipos activos"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await EquipoService.get_all(db, seccion=seccion, activo_only=activo_only)

@router.get("/{equipo_id}", response_model=EquipoOut)
async def get_equipo(
    equipo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    eq = await EquipoService.get_by_id(db, equipo_id)
    if not eq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
    return eq

@router.post("", response_model=EquipoOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def create_equipo(
    equipo_in: EquipoCreate,
    db: AsyncSession = Depends(get_db)
):
    return await EquipoService.create(db, equipo_in)

@router.put("/{equipo_id}", response_model=EquipoOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def update_equipo(
    equipo_id: int,
    equipo_in: EquipoUpdate,
    db: AsyncSession = Depends(get_db)
):
    eq = await EquipoService.update(db, equipo_id, equipo_in)
    if not eq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
    return eq

@router.delete("/{equipo_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def delete_equipo(
    equipo_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await EquipoService.delete(db, equipo_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
    return {"message": "Equipo eliminado correctamente"}
