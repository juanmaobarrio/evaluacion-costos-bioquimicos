from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from app.modules.costos_generales.models import (
    SeccionLaboratorio, GastoFijoMensual, ParametroLaboratorio, MaterialExtraccionItem, Protocolo, ProtocoloEstudio
)
from app.modules.costos_generales.schemas import (
    SeccionLaboratorioCreate, SeccionLaboratorioUpdate, SeccionLaboratorioOut,
    GastoFijoCreate, GastoFijoUpdate, GastoFijoOut,
    ParametroLaboratorioCreate, ParametroLaboratorioUpdate, ParametroLaboratorioOut,
    MaterialExtraccionItemCreate, MaterialExtraccionItemOut,
    ProtocoloCreate, ProtocoloUpdate, ProtocoloOut, ProtocoloEstudioOut
)
from app.modules.determinaciones.service import DeterminacionService
from app.modules.determinaciones.models import Determinacion, DeterminacionInsumo
from app.modules.insumos.models import Insumo
from app.modules.costos.calculator_service import CostCalculatorService, round_currency

class SeccionesService:
    @staticmethod
    async def get_all(db: AsyncSession, activo_only: bool = False) -> List[SeccionLaboratorioOut]:
        query = select(SeccionLaboratorio)
        if activo_only:
            query = query.where(SeccionLaboratorio.activo == True)
        res = await db.execute(query.order_by(SeccionLaboratorio.nombre))
        return res.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, seccion_in: SeccionLaboratorioCreate) -> SeccionLaboratorio:
        seccion = SeccionLaboratorio(**seccion_in.model_dump())
        db.add(seccion)
        await db.commit()
        await db.refresh(seccion)
        return seccion

    @staticmethod
    async def update(db: AsyncSession, seccion_id: int, seccion_in: SeccionLaboratorioUpdate) -> Optional[SeccionLaboratorio]:
        res = await db.execute(select(SeccionLaboratorio).where(SeccionLaboratorio.id == seccion_id))
        seccion = res.scalars().first()
        if not seccion:
            return None
        for k, v in seccion_in.model_dump(exclude_unset=True).items():
            setattr(seccion, k, v)
        await db.commit()
        await db.refresh(seccion)
        return seccion

    @staticmethod
    async def delete(db: AsyncSession, seccion_id: int) -> bool:
        res = await db.execute(select(SeccionLaboratorio).where(SeccionLaboratorio.id == seccion_id))
        seccion = res.scalars().first()
        if not seccion:
            return False
        await db.delete(seccion)
        await db.commit()
        return True

class GastosFijosService:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[GastoFijoOut]:
        res = await db.execute(select(GastoFijoMensual).order_by(GastoFijoMensual.categoria, GastoFijoMensual.concepto))
        return res.scalars().all()

    @staticmethod
    async def get_total_mensual_activo(db: AsyncSession) -> Decimal:
        res = await db.execute(select(func.sum(GastoFijoMensual.monto_mensual)).where(GastoFijoMensual.activo == True))
        val = res.scalar()
        return Decimal(str(val or 0))

    @staticmethod
    async def create(db: AsyncSession, gf_in: GastoFijoCreate) -> GastoFijoMensual:
        gf = GastoFijoMensual(**gf_in.model_dump())
        db.add(gf)
        await db.commit()
        await db.refresh(gf)
        return gf

    @staticmethod
    async def update(db: AsyncSession, gf_id: int, gf_in: GastoFijoUpdate) -> Optional[GastoFijoMensual]:
        res = await db.execute(select(GastoFijoMensual).where(GastoFijoMensual.id == gf_id))
        gf = res.scalars().first()
        if not gf:
            return None
        for k, v in gf_in.model_dump(exclude_unset=True).items():
            setattr(gf, k, v)
        await db.commit()
        await db.refresh(gf)
        return gf

    @staticmethod
    async def delete(db: AsyncSession, gf_id: int) -> bool:
        res = await db.execute(select(GastoFijoMensual).where(GastoFijoMensual.id == gf_id))
        gf = res.scalars().first()
        if not gf:
            return False
        await db.delete(gf)
        await db.commit()
        return True

class ParametrosService:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[ParametroLaboratorioOut]:
        res = await db.execute(select(ParametroLaboratorio).order_by(ParametroLaboratorio.categoria, ParametroLaboratorio.clave))
        return res.scalars().all()

    @staticmethod
    async def get_valor_numerico(db: AsyncSession, clave: str, default: Decimal = Decimal("0.0")) -> Decimal:
        res = await db.execute(select(ParametroLaboratorio).where(ParametroLaboratorio.clave == clave))
        param = res.scalars().first()
        if param and param.valor_numerico is not None:
            return Decimal(str(param.valor_numerico))
        return default

    @staticmethod
    async def upsert(db: AsyncSession, clave: str, valor_numerico: Optional[Decimal] = None, valor_texto: Optional[str] = None, descripcion: Optional[str] = None, categoria: str = "General") -> ParametroLaboratorio:
        res = await db.execute(select(ParametroLaboratorio).where(ParametroLaboratorio.clave == clave))
        param = res.scalars().first()
        if not param:
            param = ParametroLaboratorio(clave=clave, valor_numerico=valor_numerico, valor_texto=valor_texto, descripcion=descripcion, categoria=categoria)
            db.add(param)
        else:
            if valor_numerico is not None:
                param.valor_numerico = valor_numerico
            if valor_texto is not None:
                param.valor_texto = valor_texto
            if descripcion is not None:
                param.descripcion = descripcion
            if categoria:
                param.categoria = categoria
        await db.commit()
        await db.refresh(param)
        return param

class MaterialesExtraccionService:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[MaterialExtraccionItemOut]:
        res = await db.execute(select(MaterialExtraccionItem).options(selectinload(MaterialExtraccionItem.insumo)))
        items = res.scalars().all()
        outs = []
        for it in items:
            costo_subtotal = Decimal("0.0")
            if it.insumo:
                costo_subtotal = round_currency(it.insumo.costo_unitario_ars * it.cantidad, 4)
            outs.append(MaterialExtraccionItemOut(
                id=it.id,
                insumo_id=it.insumo_id,
                cantidad=it.cantidad,
                es_obligatorio=it.es_obligatorio,
                insumo=it.insumo,
                costo_subtotal_ars=costo_subtotal
            ))
        return outs

    @staticmethod
    async def get_costo_total_extraccion(db: AsyncSession) -> Decimal:
        items = await MaterialesExtraccionService.get_all(db)
        total = sum((it.costo_subtotal_ars for it in items), Decimal("0.0"))
        return round_currency(total, 4)

    @staticmethod
    async def add_item(db: AsyncSession, item_in: MaterialExtraccionItemCreate) -> MaterialExtraccionItem:
        item = MaterialExtraccionItem(**item_in.model_dump())
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def delete_item(db: AsyncSession, item_id: int) -> bool:
        res = await db.execute(select(MaterialExtraccionItem).where(MaterialExtraccionItem.id == item_id))
        item = res.scalars().first()
        if not item:
            return False
        await db.delete(item)
        await db.commit()
        return True

class ProtocoloService:
    @classmethod
    async def _enrich_protocolo(cls, db: AsyncSession, proto: Protocolo) -> ProtocoloOut:
        # Calcular costo determinaciones
        costo_estudios_total = Decimal("0.0")
        estudios_out = []
        for pe in proto.estudios:
            if pe.determinacion:
                det_out = DeterminacionService._enrich_out(pe.determinacion)
                costo_estudios_total += det_out.costo_unitario_total_ars
                estudios_out.append(ProtocoloEstudioOut(
                    id=pe.id,
                    determinacion_id=pe.determinacion_id,
                    determinacion=det_out
                ))

        # Costo extracción
        costo_extraccion = await MaterialesExtraccionService.get_costo_total_extraccion(db)

        # Overhead por paciente
        total_fijos = await GastosFijosService.get_total_mensual_activo(db)
        volumen_pacientes = int(await ParametrosService.get_valor_numerico(db, "PACIENTES_MENSUALES_ESTIMADOS", Decimal("1000")))

        res_calc = CostCalculatorService.calcular_costo_protocolo(
            costo_total_estudios=costo_estudios_total,
            costo_extraccion_descartables=costo_extraccion,
            total_gastos_fijos_mensuales=total_fijos,
            volumen_pacientes_mensual=volumen_pacientes
        )

        arancel = proto.arancel_sugerido_ars or Decimal("0.0")
        costo_total = res_calc["costo_total_protocolo"]
        margen_bruto = arancel - costo_total
        margen_pct = (margen_bruto / arancel * Decimal("100.0")) if arancel > Decimal("0") else Decimal("0.0")

        return ProtocoloOut(
            id=proto.id,
            nombre=proto.nombre,
            codigo=proto.codigo,
            descripcion=proto.descripcion,
            arancel_sugerido_ars=proto.arancel_sugerido_ars,
            activo=proto.activo,
            costo_determinaciones_ars=res_calc["costo_estudios"],
            costo_extraccion_descartables=res_calc["costo_extraccion"],
            costo_overhead_fijo_ars=res_calc["overhead_por_paciente"],
            costo_total_protocolo_ars=costo_total,
            margen_bruto_ars=round_currency(margen_bruto, 2),
            margen_estimado_porcentaje=round_currency(margen_pct, 2),
            estudios=estudios_out,
            created_at=proto.created_at,
            updated_at=proto.updated_at
        )

    @classmethod
    async def get_all(cls, db: AsyncSession) -> List[ProtocoloOut]:
        query = select(Protocolo).options(
            selectinload(Protocolo.estudios).selectinload(ProtocoloEstudio.determinacion).selectinload(Determinacion.equipo),
            selectinload(Protocolo.estudios).selectinload(ProtocoloEstudio.determinacion).selectinload(Determinacion.insumos_asociados).selectinload(DeterminacionInsumo.insumo)
        ).order_by(Protocolo.nombre)
        res = await db.execute(query)
        protos = res.scalars().all()
        return [await cls._enrich_protocolo(db, p) for p in protos]

    @classmethod
    async def get_by_id(cls, db: AsyncSession, proto_id: int) -> Optional[ProtocoloOut]:
        query = select(Protocolo).options(
            selectinload(Protocolo.estudios).selectinload(ProtocoloEstudio.determinacion).selectinload(Determinacion.equipo),
            selectinload(Protocolo.estudios).selectinload(ProtocoloEstudio.determinacion).selectinload(Determinacion.insumos_asociados).selectinload(DeterminacionInsumo.insumo)
        ).where(Protocolo.id == proto_id)
        res = await db.execute(query)
        proto = res.scalars().first()
        return await cls._enrich_protocolo(db, proto) if proto else None

    @classmethod
    async def create(cls, db: AsyncSession, proto_in: ProtocoloCreate) -> ProtocoloOut:
        data = proto_in.model_dump(exclude={"determinacion_ids"})
        proto = Protocolo(**data)
        db.add(proto)
        await db.flush()

        for det_id in proto_in.determinacion_ids:
            pe = ProtocoloEstudio(protocolo_id=proto.id, determinacion_id=det_id)
            db.add(pe)

        await db.commit()
        return await cls.get_by_id(db, proto.id)

    @classmethod
    async def update(cls, db: AsyncSession, proto_id: int, proto_in: ProtocoloUpdate) -> Optional[ProtocoloOut]:
        res = await db.execute(select(Protocolo).where(Protocolo.id == proto_id))
        proto = res.scalars().first()
        if not proto:
            return None

        update_data = proto_in.model_dump(exclude_unset=True, exclude={"determinacion_ids"})
        for k, v in update_data.items():
            setattr(proto, k, v)

        if proto_in.determinacion_ids is not None:
            await db.execute(delete(ProtocoloEstudio).where(ProtocoloEstudio.protocolo_id == proto_id))
            await db.flush()
            for det_id in proto_in.determinacion_ids:
                pe = ProtocoloEstudio(protocolo_id=proto.id, determinacion_id=det_id)
                db.add(pe)

        await db.commit()
        return await cls.get_by_id(db, proto.id)

    @classmethod
    async def delete(cls, db: AsyncSession, proto_id: int) -> bool:
        res = await db.execute(select(Protocolo).where(Protocolo.id == proto_id))
        proto = res.scalars().first()
        if not proto:
            return False
        await db.delete(proto)
        await db.commit()
        return True
