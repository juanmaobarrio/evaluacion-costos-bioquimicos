from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.modules.configuracion.models import LaboratorioReferencia, TipoInsumoCatalogo
from app.modules.configuracion.schemas import (
    LaboratorioReferenciaCreate, LaboratorioReferenciaUpdate,
    TipoInsumoCatalogoCreate, TipoInsumoCatalogoUpdate
)

class LaboratoriosReferenciaService:
    @staticmethod
    async def get_all(db: AsyncSession, activo_only: bool = False) -> List[LaboratorioReferencia]:
        query = select(LaboratorioReferencia)
        if activo_only:
            query = query.where(LaboratorioReferencia.activo == True)
        res = await db.execute(query.order_by(LaboratorioReferencia.nombre))
        return res.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, lab_id: int) -> Optional[LaboratorioReferencia]:
        res = await db.execute(select(LaboratorioReferencia).where(LaboratorioReferencia.id == lab_id))
        return res.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, lab_in: LaboratorioReferenciaCreate) -> LaboratorioReferencia:
        # Verificar duplicado de nombre
        existing = await db.execute(select(LaboratorioReferencia).where(LaboratorioReferencia.nombre == lab_in.nombre))
        if existing.scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un laboratorio de referencia con el nombre '{lab_in.nombre}'")
        lab = LaboratorioReferencia(**lab_in.model_dump())
        db.add(lab)
        await db.commit()
        await db.refresh(lab)
        return lab

    @staticmethod
    async def update(db: AsyncSession, lab_id: int, lab_in: LaboratorioReferenciaUpdate) -> Optional[LaboratorioReferencia]:
        lab = await LaboratoriosReferenciaService.get_by_id(db, lab_id)
        if not lab:
            return None
        update_data = lab_in.model_dump(exclude_unset=True)
        if "nombre" in update_data and update_data["nombre"] != lab.nombre:
            existing = await db.execute(select(LaboratorioReferencia).where(LaboratorioReferencia.nombre == update_data["nombre"]))
            if existing.scalars().first():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un laboratorio con el nombre '{update_data['nombre']}'")
        for k, v in update_data.items():
            setattr(lab, k, v)
        await db.commit()
        await db.refresh(lab)
        return lab

    @staticmethod
    async def delete(db: AsyncSession, lab_id: int) -> bool:
        lab = await LaboratoriosReferenciaService.get_by_id(db, lab_id)
        if not lab:
            return False
        # Verificar si hay determinaciones que apunten a este laboratorio
        from app.modules.determinaciones.models import Determinacion
        count_query = select(func.count(Determinacion.id)).where(Determinacion.laboratorio_referencia_id == lab_id)
        count_res = await db.execute(count_query)
        in_use_count = count_res.scalar() or 0
        if in_use_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el laboratorio '{lab.nombre}' porque está asignado a {in_use_count} determinación(es). Desasócielo primero o desactívelo."
            )
        await db.delete(lab)
        await db.commit()
        return True

class TiposInsumoService:
    @staticmethod
    async def get_all(db: AsyncSession, activo_only: bool = False) -> List[TipoInsumoCatalogo]:
        query = select(TipoInsumoCatalogo)
        if activo_only:
            query = query.where(TipoInsumoCatalogo.activo == True)
        res = await db.execute(query.order_by(TipoInsumoCatalogo.orden, TipoInsumoCatalogo.nombre))
        return res.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, tipo_id: int) -> Optional[TipoInsumoCatalogo]:
        res = await db.execute(select(TipoInsumoCatalogo).where(TipoInsumoCatalogo.id == tipo_id))
        return res.scalars().first()

    @staticmethod
    async def get_by_clave(db: AsyncSession, clave: str) -> Optional[TipoInsumoCatalogo]:
        res = await db.execute(select(TipoInsumoCatalogo).where(TipoInsumoCatalogo.clave == clave.lower().strip()))
        return res.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, tipo_in: TipoInsumoCatalogoCreate) -> TipoInsumoCatalogo:
        clave_norm = tipo_in.clave.lower().strip().replace(" ", "_")
        existing = await db.execute(select(TipoInsumoCatalogo).where(TipoInsumoCatalogo.clave == clave_norm))
        if existing.scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un tipo de insumo con la clave '{clave_norm}'")
        data = tipo_in.model_dump()
        data["clave"] = clave_norm
        tipo = TipoInsumoCatalogo(**data)
        db.add(tipo)
        await db.commit()
        await db.refresh(tipo)
        return tipo

    @staticmethod
    async def update(db: AsyncSession, tipo_id: int, tipo_in: TipoInsumoCatalogoUpdate) -> Optional[TipoInsumoCatalogo]:
        tipo = await TiposInsumoService.get_by_id(db, tipo_id)
        if not tipo:
            return None
        update_data = tipo_in.model_dump(exclude_unset=True)
        if "clave" in update_data:
            update_data["clave"] = update_data["clave"].lower().strip().replace(" ", "_")
            if update_data["clave"] != tipo.clave:
                existing = await db.execute(select(TipoInsumoCatalogo).where(TipoInsumoCatalogo.clave == update_data["clave"]))
                if existing.scalars().first():
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un tipo con la clave '{update_data['clave']}'")
        for k, v in update_data.items():
            setattr(tipo, k, v)
        await db.commit()
        await db.refresh(tipo)
        return tipo

    @staticmethod
    async def delete(db: AsyncSession, tipo_id: int) -> bool:
        tipo = await TiposInsumoService.get_by_id(db, tipo_id)
        if not tipo:
            return False
        # Verificar si hay insumos que usen esta clave
        from app.modules.insumos.models import Insumo
        count_query = select(func.count(Insumo.id)).where(Insumo.tipo == tipo.clave)
        count_res = await db.execute(count_query)
        in_use_count = count_res.scalar() or 0
        if in_use_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el tipo '{tipo.nombre}' porque {in_use_count} insumo(s) lo están utilizando. Modifique primero los insumos o desactive el tipo."
            )
        await db.delete(tipo)
        await db.commit()
        return True
