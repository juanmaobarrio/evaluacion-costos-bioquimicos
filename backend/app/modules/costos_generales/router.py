from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.service import get_current_user, require_role
from app.modules.auth.models import UserRole
from app.modules.costos_generales.schemas import (
    SeccionLaboratorioCreate, SeccionLaboratorioUpdate, SeccionLaboratorioOut,
    GastoFijoCreate, GastoFijoUpdate, GastoFijoOut,
    ParametroLaboratorioOut, ParametroLaboratorioUpdate,
    MaterialExtraccionItemCreate, MaterialExtraccionItemOut,
    ProtocoloCreate, ProtocoloUpdate, ProtocoloOut
)
from app.modules.costos_generales.service import (
    SeccionesService, GastosFijosService, ParametrosService, MaterialesExtraccionService, ProtocoloService
)

router = APIRouter(tags=["Gastos Fijos, Parámetros y Protocolos"])

# --- SECCIONES DEL LABORATORIO ---
@router.get("/secciones", response_model=List[SeccionLaboratorioOut])
@router.get("/secciones/", response_model=List[SeccionLaboratorioOut], include_in_schema=False)
async def list_secciones(activo_only: bool = False, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await SeccionesService.get_all(db, activo_only=activo_only)

@router.post("/secciones", response_model=SeccionLaboratorioOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
@router.post("/secciones/", response_model=SeccionLaboratorioOut, include_in_schema=False, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def create_seccion(seccion_in: SeccionLaboratorioCreate, db: AsyncSession = Depends(get_db)):
    return await SeccionesService.create(db, seccion_in)

@router.put("/secciones/{seccion_id}", response_model=SeccionLaboratorioOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def update_seccion(seccion_id: int, seccion_in: SeccionLaboratorioUpdate, db: AsyncSession = Depends(get_db)):
    seccion = await SeccionesService.update(db, seccion_id, seccion_in)
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    return seccion

@router.delete("/secciones/{seccion_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def delete_seccion(seccion_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await SeccionesService.delete(db, seccion_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    return {"message": "Sección eliminada"}

# --- GASTOS FIJOS ---
@router.get("/gastos-fijos", response_model=List[GastoFijoOut])
async def list_gastos_fijos(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await GastosFijosService.get_all(db)

@router.post("/gastos-fijos", response_model=GastoFijoOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def create_gasto_fijo(gf_in: GastoFijoCreate, db: AsyncSession = Depends(get_db)):
    return await GastosFijosService.create(db, gf_in)

@router.put("/gastos-fijos/{gf_id}", response_model=GastoFijoOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def update_gasto_fijo(gf_id: int, gf_in: GastoFijoUpdate, db: AsyncSession = Depends(get_db)):
    gf = await GastosFijosService.update(db, gf_id, gf_in)
    if not gf:
        raise HTTPException(status_code=404, detail="Gasto fijo no encontrado")
    return gf

@router.delete("/gastos-fijos/{gf_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def delete_gasto_fijo(gf_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await GastosFijosService.delete(db, gf_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Gasto fijo no encontrado")
    return {"message": "Gasto fijo eliminado"}

# --- PARÁMETROS DE LABORATORIO ---
@router.get("/parametros", response_model=List[ParametroLaboratorioOut])
async def list_parametros(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await ParametrosService.get_all(db)

@router.put("/parametros/{clave}", response_model=ParametroLaboratorioOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def update_parametro(clave: str, param_in: ParametroLaboratorioUpdate, db: AsyncSession = Depends(get_db)):
    return await ParametrosService.upsert(
        db, clave=clave,
        valor_numerico=param_in.valor_numerico,
        valor_texto=param_in.valor_texto,
        descripcion=param_in.descripcion,
        categoria=param_in.categoria or "General"
    )

# --- MATERIALES DE EXTRACCIÓN ---
@router.get("/materiales-extraccion", response_model=List[MaterialExtraccionItemOut])
async def list_materiales_extraccion(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await MaterialesExtraccionService.get_all(db)

@router.post("/materiales-extraccion", response_model=MaterialExtraccionItemOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def add_material_extraccion(item_in: MaterialExtraccionItemCreate, db: AsyncSession = Depends(get_db)):
    item = await MaterialesExtraccionService.add_item(db, item_in)
    items = await MaterialesExtraccionService.get_all(db)
    for it in items:
        if it.id == item.id:
            return it
    return item

@router.delete("/materiales-extraccion/{item_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def delete_material_extraccion(item_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await MaterialesExtraccionService.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"message": "Item eliminado"}

# --- PROTOCOLOS / PERFILES ---
@router.get("/protocolos", response_model=List[ProtocoloOut])
async def list_protocolos(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await ProtocoloService.get_all(db)

@router.get("/protocolos/{proto_id}", response_model=ProtocoloOut)
async def get_protocolo(proto_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    p = await ProtocoloService.get_by_id(db, proto_id)
    if not p:
        raise HTTPException(status_code=404, detail="Protocolo no encontrado")
    return p

@router.post("/protocolos", response_model=ProtocoloOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def create_protocolo(proto_in: ProtocoloCreate, db: AsyncSession = Depends(get_db)):
    return await ProtocoloService.create(db, proto_in)

@router.put("/protocolos/{proto_id}", response_model=ProtocoloOut, dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.BIOQUIMICO]))])
async def update_protocolo(proto_id: int, proto_in: ProtocoloUpdate, db: AsyncSession = Depends(get_db)):
    p = await ProtocoloService.update(db, proto_id, proto_in)
    if not p:
        raise HTTPException(status_code=404, detail="Protocolo no encontrado")
    return p

@router.delete("/protocolos/{proto_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def delete_protocolo(proto_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await ProtocoloService.delete(db, proto_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Protocolo no encontrado")
    return {"message": "Protocolo eliminado"}
