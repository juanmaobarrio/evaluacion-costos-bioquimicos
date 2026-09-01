from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.modules.determinaciones.models import Determinacion, DeterminacionInsumo
from app.modules.determinaciones.schemas import DeterminacionCreate, DeterminacionUpdate, DeterminacionOut, DeterminacionInsumoOut
from app.modules.equipos.models import Equipo
from app.modules.equipos.service import EquipoService
from app.modules.insumos.models import Insumo
from app.modules.costos_generales.models import ParametroLaboratorio
from app.modules.costos.calculator_service import CostCalculatorService, round_currency

class DeterminacionService:
    @staticmethod
    async def get_costo_hora_mano_obra(db: AsyncSession) -> Decimal:
        query = select(ParametroLaboratorio).where(ParametroLaboratorio.clave == "VALOR_HORA_TECNICO")
        res = await db.execute(query)
        param = res.scalars().first()
        if param and param.valor_numerico:
            return Decimal(str(param.valor_numerico))
        return Decimal("5000.00") # Default fallback ARS / hora

    @classmethod
    async def _recalcular_costos(cls, db: AsyncSession, determinacion: Determinacion) -> Determinacion:
        # 1. Obtener insumos y cantidades asociadas
        insumos_items = []
        for det_ins in determinacion.insumos_asociados:
            if det_ins.insumo:
                insumos_items.append({
                    "costo_unitario_ars": det_ins.insumo.costo_unitario_ars,
                    "costo_por_determinacion_usd": det_ins.insumo.costo_por_determinacion_usd,
                    "cantidad": det_ins.cantidad_requerida
                })

        # 2. Obtener costo unitario del equipo asignado
        costo_equipo_unit = Decimal("0.0")
        if determinacion.equipo_id:
            eq = await EquipoService.get_by_id(db, determinacion.equipo_id)
            if eq:
                costo_equipo_unit = eq.costo_unitario_por_test

        # 3. Obtener costo hora mano de obra
        costo_hora = await cls.get_costo_hora_mano_obra(db)

        # 4. Calcular
        calc = CostCalculatorService.calcular_costo_determinacion(
            insumos_con_cantidad=insumos_items,
            costo_equipo_por_test=costo_equipo_unit,
            tasa_repeticion_porcentaje=determinacion.tasa_repeticion_porcentaje or Decimal("0.0"),
            tiempo_proceso_minutos=determinacion.tiempo_proceso_minutos or Decimal("0.0"),
            costo_hora_mano_obra=costo_hora,
            tipo_cambio_usd=Decimal("1200.0")
        )

        determinacion.costo_reactivos_ars = calc["costo_reactivos_puro"]
        determinacion.costo_reactivos_usd = calc["costo_reactivos_usd"]
        determinacion.costo_repeticion_ars = calc["costo_repeticion_incremental"]
        determinacion.costo_equipo_ars = calc["costo_equipo"]
        determinacion.costo_equipo_usd = calc["costo_equipo_usd"]
        determinacion.costo_mano_obra_ars = calc["costo_mano_obra"]
        determinacion.costo_mano_obra_usd = calc["costo_mano_obra_usd"]
        determinacion.costo_unitario_total_ars = calc["costo_unitario_total"]
        determinacion.costo_unitario_total_usd = calc["costo_unitario_total_usd"]

        return determinacion

    @classmethod
    def _enrich_out(cls, det: Determinacion) -> DeterminacionOut:
        # Calcular márgenes
        arancel_ars = det.arancel_referencia_ars or Decimal("0.0")
        arancel_usd = det.arancel_referencia_usd or (arancel_ars / Decimal("1200.0") if arancel_ars > 0 else Decimal("0.0"))
        costo_total_ars = det.costo_unitario_total_ars or Decimal("0.0")
        costo_total_usd = det.costo_unitario_total_usd or (costo_total_ars / Decimal("1200.0") if costo_total_ars > 0 else Decimal("0.0"))

        margen_bruto_ars = arancel_ars - costo_total_ars
        margen_bruto_usd = arancel_usd - costo_total_usd
        margen_pct = (margen_bruto_ars / arancel_ars * Decimal("100.0")) if arancel_ars > Decimal("0") else Decimal("0.0")

        # Insumos asociados enriquecidos con subtotales
        ins_outs = []
        for item in (det.insumos_asociados or []):
            costo_subtotal_ars = Decimal("0.0")
            costo_subtotal_usd = Decimal("0.0")
            if item.insumo:
                costo_subtotal_ars = round_currency(item.insumo.costo_unitario_ars * item.cantidad_requerida, 4)
                costo_subtotal_usd = round_currency(item.insumo.costo_por_determinacion_usd * item.cantidad_requerida, 6)
            ins_outs.append(DeterminacionInsumoOut(
                id=item.id,
                insumo_id=item.insumo_id,
                cantidad_requerida=item.cantidad_requerida,
                insumo=item.insumo,
                costo_subtotal_ars=costo_subtotal_ars,
                costo_subtotal_usd=costo_subtotal_usd
            ))

        return DeterminacionOut(
            id=det.id,
            codigo=det.codigo,
            codigo_nomenclador=det.codigo_nomenclador,
            nombre=det.nombre,
            seccion=det.seccion,
            equipo_id=det.equipo_id,
            tiempo_proceso_minutos=det.tiempo_proceso_minutos,
            tasa_repeticion_porcentaje=det.tasa_repeticion_porcentaje,
            arancel_referencia_ars=det.arancel_referencia_ars,
            arancel_referencia_usd=round_currency(arancel_usd, 4),
            activo=det.activo,
            notas=det.notas,
            costo_reactivos_ars=det.costo_reactivos_ars,
            costo_reactivos_usd=det.costo_reactivos_usd,
            costo_equipo_ars=det.costo_equipo_ars,
            costo_equipo_usd=det.costo_equipo_usd,
            costo_repeticion_ars=det.costo_repeticion_ars,
            costo_mano_obra_ars=det.costo_mano_obra_ars,
            costo_mano_obra_usd=det.costo_mano_obra_usd,
            costo_unitario_total_ars=det.costo_unitario_total_ars,
            costo_unitario_total_usd=det.costo_unitario_total_usd,
            margen_estimado_porcentaje=round_currency(margen_pct, 2),
            margen_bruto_ars=round_currency(margen_bruto_ars, 2),
            margen_bruto_usd=round_currency(margen_bruto_usd, 4),
            equipo=det.equipo,
            insumos_asociados=ins_outs,
            created_at=det.created_at,
            updated_at=det.updated_at
        )

    @classmethod
    async def get_all(
        cls,
        db: AsyncSession,
        seccion: Optional[str] = None,
        equipo_id: Optional[int] = None,
        search: Optional[str] = None,
        activo_only: bool = False
    ) -> List[DeterminacionOut]:
        query = select(Determinacion).options(
            selectinload(Determinacion.equipo),
            selectinload(Determinacion.insumos_asociados).selectinload(DeterminacionInsumo.insumo)
        )
        if seccion:
            query = query.where(Determinacion.seccion == seccion)
        if equipo_id:
            query = query.where(Determinacion.equipo_id == equipo_id)
        if activo_only:
            query = query.where(Determinacion.activo == True)
        if search:
            query = query.where(
                (Determinacion.nombre.ilike(f"%{search}%")) |
                (Determinacion.codigo.ilike(f"%{search}%")) |
                (Determinacion.codigo_nomenclador.ilike(f"%{search}%"))
            )
        result = await db.execute(query.order_by(Determinacion.nombre))
        dets = result.scalars().all()
        return [cls._enrich_out(d) for d in dets]

    @classmethod
    async def get_by_id(cls, db: AsyncSession, det_id: int) -> Optional[DeterminacionOut]:
        query = select(Determinacion).options(
            selectinload(Determinacion.equipo),
            selectinload(Determinacion.insumos_asociados).selectinload(DeterminacionInsumo.insumo)
        ).where(Determinacion.id == det_id)
        result = await db.execute(query)
        det = result.scalars().first()
        return cls._enrich_out(det) if det else None

    @classmethod
    async def create(cls, db: AsyncSession, det_in: DeterminacionCreate) -> DeterminacionOut:
        data = det_in.model_dump(exclude={"insumos"})
        det = Determinacion(**data)
        db.add(det)
        await db.flush()

        # Insumos
        for ins in det_in.insumos:
            item = DeterminacionInsumo(
                determinacion_id=det.id,
                insumo_id=ins.insumo_id,
                cantidad_requerida=ins.cantidad_requerida
            )
            db.add(item)

        await db.flush()

        # Cargar relaciones para cálculo
        await db.refresh(det, ["insumos_asociados", "equipo"])
        for rel in det.insumos_asociados:
            await db.refresh(rel, ["insumo"])

        det = await cls._recalcular_costos(db, det)
        await db.commit()
        await db.refresh(det)
        return await cls.get_by_id(db, det.id)

    @classmethod
    async def update(cls, db: AsyncSession, det_id: int, det_in: DeterminacionUpdate) -> Optional[DeterminacionOut]:
        query = select(Determinacion).options(
            selectinload(Determinacion.insumos_asociados).selectinload(DeterminacionInsumo.insumo),
            selectinload(Determinacion.equipo)
        ).where(Determinacion.id == det_id)
        result = await db.execute(query)
        det = result.scalars().first()
        if not det:
            return None

        update_data = det_in.model_dump(exclude_unset=True, exclude={"insumos"})
        for k, v in update_data.items():
            setattr(det, k, v)

        # Actualizar lista de insumos si viene provista
        if det_in.insumos is not None:
            # Borrar existentes
            await db.execute(delete(DeterminacionInsumo).where(DeterminacionInsumo.determinacion_id == det_id))
            await db.flush()
            for ins in det_in.insumos:
                item = DeterminacionInsumo(
                    determinacion_id=det.id,
                    insumo_id=ins.insumo_id,
                    cantidad_requerida=ins.cantidad_requerida
                )
                db.add(item)
            await db.flush()

        await db.refresh(det, ["insumos_asociados", "equipo"])
        for rel in det.insumos_asociados:
            await db.refresh(rel, ["insumo"])

        det = await cls._recalcular_costos(db, det)
        await db.commit()
        return await cls.get_by_id(db, det.id)

    @classmethod
    async def delete(cls, db: AsyncSession, det_id: int) -> bool:
        query = select(Determinacion).where(Determinacion.id == det_id)
        result = await db.execute(query)
        det = result.scalars().first()
        if not det:
            return False
        await db.delete(det)
        await db.commit()
        return True

    @classmethod
    async def recalcular_todas(cls, db: AsyncSession) -> int:
        """Recalcula los costos de todas las determinaciones de la base de datos."""
        query = select(Determinacion).options(
            selectinload(Determinacion.insumos_asociados).selectinload(DeterminacionInsumo.insumo),
            selectinload(Determinacion.equipo)
        )
        result = await db.execute(query)
        dets = result.scalars().all()
        for det in dets:
            await cls._recalcular_costos(db, det)
        await db.commit()
        return len(dets)
