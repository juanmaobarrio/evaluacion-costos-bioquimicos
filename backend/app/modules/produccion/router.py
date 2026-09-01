from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.service import get_current_user, require_role
from app.modules.auth.models import UserRole
from app.modules.produccion.schemas import (
    ProduccionBatchImport, ProduccionRegistroCreate, ProduccionRegistroOut, ConciliacionItemOut
)
from app.modules.produccion.service import ProduccionService

router = APIRouter(prefix="/produccion", tags=["Producción, Compras y Webhooks"])

@router.post("/webhook-import")
async def webhook_import_produccion(
    batch: ProduccionBatchImport,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint habilitado para automatizaciones de n8n / LIS."""
    return await ProduccionService.importar_batch_webhook(db, batch)

@router.post("", response_model=ProduccionRegistroOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def registrar_produccion_manual(
    item_in: ProduccionRegistroCreate,
    db: AsyncSession = Depends(get_db)
):
    return await ProduccionService.registrar_produccion(db, item_in)

@router.get("/periodo", response_model=List[ProduccionRegistroOut])
async def get_produccion_periodo(
    mes: int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await ProduccionService.get_produccion_periodo(db, mes, anio)

@router.get("/conciliacion", response_model=List[ConciliacionItemOut])
async def get_conciliacion_periodo(
    mes: int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await ProduccionService.calcular_conciliacion_insumos(db, mes, anio)
