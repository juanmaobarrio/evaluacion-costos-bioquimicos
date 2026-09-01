from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.service import get_current_user, require_role
from app.modules.auth.models import UserRole
from app.modules.determinaciones.schemas import DeterminacionCreate, DeterminacionUpdate, DeterminacionOut
from app.modules.determinaciones.service import DeterminacionService

router = APIRouter(prefix="/determinaciones", tags=["Catálogo de Determinaciones"])

@router.get("", response_model=List[DeterminacionOut])
async def list_determinaciones(
    seccion: Optional[str] = Query(None, description="Filtrar por sección"),
    equipo_id: Optional[int] = Query(None, description="Filtrar por equipo"),
    search: Optional[str] = Query(None, description="Buscar por nombre o código"),
    activo_only: bool = Query(False, description="Solo determinaciones activas"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await DeterminacionService.get_all(
        db, seccion=seccion, equipo_id=equipo_id, search=search, activo_only=activo_only
    )

@router.get("/{det_id}", response_model=DeterminacionOut)
async def get_determinacion(
    det_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    det = await DeterminacionService.get_by_id(db, det_id)
    if not det:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Determinación no encontrada")
    return det

@router.post("", response_model=DeterminacionOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def create_determinacion(
    det_in: DeterminacionCreate,
    db: AsyncSession = Depends(get_db)
):
    return await DeterminacionService.create(db, det_in)

@router.put("/{det_id}", response_model=DeterminacionOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def update_determinacion(
    det_id: int,
    det_in: DeterminacionUpdate,
    db: AsyncSession = Depends(get_db)
):
    det = await DeterminacionService.update(db, det_id, det_in)
    if not det:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Determinación no encontrada")
    return det

@router.delete("/{det_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def delete_determinacion(
    det_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await DeterminacionService.delete(db, det_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Determinación no encontrada")
    return {"message": "Determinación eliminada correctamente"}

@router.post("/recalcular-todos", dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def recalcular_todas(db: AsyncSession = Depends(get_db)):
    count = await DeterminacionService.recalcular_todas(db)
    return {"message": f"Se recalcularon exitosamente {count} determinaciones"}
