from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.modules.produccion.models import RegistroProduccionMensual, RegistroComprasMensual
from app.modules.produccion.schemas import (
    ProduccionBatchImport, ProduccionRegistroCreate, ProduccionRegistroOut, ConciliacionItemOut
)
from app.modules.determinaciones.models import Determinacion, DeterminacionInsumo
from app.modules.determinaciones.service import DeterminacionService
from app.modules.insumos.models import Insumo
from app.modules.costos.calculator_service import round_currency

class ProduccionService:
    @staticmethod
    async def registrar_produccion(db: AsyncSession, item_in: ProduccionRegistroCreate) -> RegistroProduccionMensual:
        det = await DeterminacionService.get_by_id(db, item_in.determinacion_id)
        costo_unit = det.costo_unitario_total_ars if det else Decimal("0.0")
        costo_total = costo_unit * Decimal(str(item_in.cantidad_estudios_realizados))

        reg = RegistroProduccionMensual(
            periodo_mes=item_in.periodo_mes,
            periodo_anio=item_in.periodo_anio,
            determinacion_id=item_in.determinacion_id,
            cantidad_estudios_realizados=item_in.cantidad_estudios_realizados,
            costo_unitario_historico_ars=costo_unit,
            costo_total_mes_ars=costo_total,
            fuente=item_in.fuente,
            notas=item_in.notas
        )
        db.add(reg)
        await db.commit()
        await db.refresh(reg)
        return reg

    @staticmethod
    async def importar_batch_webhook(db: AsyncSession, batch: ProduccionBatchImport) -> Dict[str, Any]:
        procesados = 0
        errores = []

        # Cachear determinaciones por id y codigo
        res = await db.execute(select(Determinacion).options(
            selectinload(Determinacion.insumos_asociados).selectinload(DeterminacionInsumo.insumo),
            selectinload(Determinacion.equipo)
        ))
        dets = res.scalars().all()
        det_map_by_id = {d.id: d for d in dets}
        det_map_by_code = {d.codigo.upper(): d for d in dets if d.codigo}

        for item in batch.items:
            target_det = None
            key = item.determinacion_codigo_o_id
            if isinstance(key, int) or (isinstance(key, str) and key.isdigit()):
                target_det = det_map_by_id.get(int(key))
            if not target_det and isinstance(key, str):
                target_det = det_map_by_code.get(key.strip().upper())

            if not target_det:
                errores.append(f"Determinación no identificada: {key}")
                continue

            costo_unit = target_det.costo_unitario_total_ars or Decimal("0.0")
            costo_total = costo_unit * Decimal(str(item.cantidad_estudios))

            # Upsert o insertar
            q_exist = await db.execute(
                select(RegistroProduccionMensual).where(
                    and_(
                        RegistroProduccionMensual.periodo_mes == batch.periodo_mes,
                        RegistroProduccionMensual.periodo_anio == batch.periodo_anio,
                        RegistroProduccionMensual.determinacion_id == target_det.id
                    )
                )
            )
            existente = q_exist.scalars().first()
            if existente:
                existente.cantidad_estudios_realizados = item.cantidad_estudios
                existente.costo_unitario_historico_ars = costo_unit
                existente.costo_total_mes_ars = costo_total
                existente.fuente = batch.fuente
            else:
                nuevo = RegistroProduccionMensual(
                    periodo_mes=batch.periodo_mes,
                    periodo_anio=batch.periodo_anio,
                    determinacion_id=target_det.id,
                    cantidad_estudios_realizados=item.cantidad_estudios,
                    costo_unitario_historico_ars=costo_unit,
                    costo_total_mes_ars=costo_total,
                    fuente=batch.fuente
                )
                db.add(nuevo)
            procesados += 1

        await db.commit()
        return {
            "status": "success",
            "periodo": f"{batch.periodo_mes}/{batch.periodo_anio}",
            "registros_procesados": procesados,
            "errores": errores
        }

    @staticmethod
    async def get_produccion_periodo(db: AsyncSession, mes: int, anio: int) -> List[RegistroProduccionMensual]:
        query = select(RegistroProduccionMensual).options(
            selectinload(RegistroProduccionMensual.determinacion).selectinload(Determinacion.equipo),
            selectinload(RegistroProduccionMensual.determinacion).selectinload(Determinacion.insumos_asociados).selectinload(DeterminacionInsumo.insumo)
        ).where(
            and_(
                RegistroProduccionMensual.periodo_mes == mes,
                RegistroProduccionMensual.periodo_anio == anio
            )
        )
        res = await db.execute(query)
        return res.scalars().all()

    @staticmethod
    async def calcular_conciliacion_insumos(db: AsyncSession, mes: int, anio: int) -> List[ConciliacionItemOut]:
        """
        Calcula la comparación entre el consumo teórico estimado por producción y las compras reales registradas.
        """
        # 1. Obtener registros de producción del mes
        producciones = await ProduccionService.get_produccion_periodo(db, mes, anio)
        
        # 2. Mapear consumo teórico de cada insumo
        teorico_unidades: Dict[int, Decimal] = {}
        insumos_dict: Dict[int, Insumo] = {}

        for prod in producciones:
            cant_estudios = Decimal(str(prod.cantidad_estudios_realizados))
            det = prod.determinacion
            if not det:
                continue
            factor_rep = Decimal("1.0") + ((det.tasa_repeticion_porcentaje or Decimal("0.0")) / Decimal("100.0"))
            
            for item in det.insumos_asociados:
                ins_id = item.insumo_id
                insumos_dict[ins_id] = item.insumo
                cant_req = item.cantidad_requerida * factor_rep * cant_estudios
                teorico_unidades[ins_id] = teorico_unidades.get(ins_id, Decimal("0.0")) + cant_req

        # 3. Obtener compras reales del mes
        q_compras = await db.execute(
            select(RegistroComprasMensual).options(selectinload(RegistroComprasMensual.insumo)).where(
                and_(
                    RegistroComprasMensual.periodo_mes == mes,
                    RegistroComprasMensual.periodo_anio == anio
                )
            )
        )
        compras = q_compras.scalars().all()
        compras_unidades: Dict[int, Decimal] = {}
        compras_ars: Dict[int, Decimal] = {}
        for c in compras:
            compras_unidades[c.insumo_id] = compras_unidades.get(c.insumo_id, Decimal("0.0")) + c.cantidad_comprada
            compras_ars[c.insumo_id] = compras_ars.get(c.insumo_id, Decimal("0.0")) + c.monto_total_ars
            if c.insumo:
                insumos_dict[c.insumo_id] = c.insumo

        # 4. Construir resultado comparativo
        todos_insumos_ids = set(teorico_unidades.keys()).union(set(compras_unidades.keys()))
        resultado = []

        for i_id in todos_insumos_ids:
            ins = insumos_dict.get(i_id)
            nombre = ins.nombre if ins else f"Insumo #{i_id}"
            costo_unit = ins.costo_unitario_ars if ins else Decimal("0.0")

            teo_u = teorico_unidades.get(i_id, Decimal("0.0"))
            teo_ars = teo_u * costo_unit

            comp_u = compras_unidades.get(i_id, Decimal("0.0"))
            comp_ars = compras_ars.get(i_id, Decimal("0.0"))

            desvio_u = comp_u - teo_u
            desvio_ars = comp_ars - teo_ars
            desvio_pct = ((comp_u - teo_u) / teo_u * Decimal("100.0")) if teo_u > 0 else Decimal("0.0")

            alerta = abs(desvio_pct) > Decimal("15.0") # Alerta si supera el 15% de desvío

            resultado.append(ConciliacionItemOut(
                insumo_id=i_id,
                insumo_nombre=nombre,
                consumo_teorico_unidades=round_currency(teo_u, 2),
                consumo_teorico_ars=round_currency(teo_ars, 2),
                compras_reales_unidades=round_currency(comp_u, 2),
                compras_reales_ars=round_currency(comp_ars, 2),
                desvio_unidades=round_currency(desvio_u, 2),
                desvio_ars=round_currency(desvio_ars, 2),
                desvio_porcentaje=round_currency(desvio_pct, 2),
                alerta=alerta
            ))

        return resultado
