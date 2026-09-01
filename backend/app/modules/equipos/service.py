from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.modules.equipos.models import Equipo
from app.modules.equipos.schemas import EquipoCreate, EquipoUpdate, EquipoOut
from app.modules.costos.calculator_service import CostCalculatorService

class EquipoService:
    @staticmethod
    def _enrich_equipo(equipo: Equipo) -> EquipoOut:
        res = CostCalculatorService.calcular_costos_equipo(
            costo_alquiler=equipo.costo_alquiler_mensual,
            costo_mantenimiento=equipo.costo_mantenimiento_mensual,
            costo_amortizacion=equipo.costo_amortizacion_mensual,
            costo_calibracion_controles=equipo.costo_calibracion_controles_mensual,
            consumibles_mantenimiento=equipo.consumibles_mantenimiento or [],
            volumen_mensual=equipo.volumen_mensual_estimado,
            moneda=equipo.moneda.value if hasattr(equipo.moneda, "value") else str(equipo.moneda or "USD"),
            tipo_cambio_usd=equipo.tipo_cambio_al_costear or Decimal("1200.0")
        )
        data = {
            "id": equipo.id,
            "nombre": equipo.nombre,
            "marca": equipo.marca,
            "modelo": equipo.modelo,
            "seccion": equipo.seccion,
            "moneda": equipo.moneda,
            "tipo_cambio_al_costear": equipo.tipo_cambio_al_costear,
            "costo_alquiler_mensual": equipo.costo_alquiler_mensual,
            "costo_mantenimiento_mensual": equipo.costo_mantenimiento_mensual,
            "costo_amortizacion_mensual": equipo.costo_amortizacion_mensual,
            "costo_calibracion_controles_mensual": equipo.costo_calibracion_controles_mensual,
            "volumen_mensual_estimado": equipo.volumen_mensual_estimado,
            "consumibles_mantenimiento": equipo.consumibles_mantenimiento or [],
            "activo": equipo.activo,
            "notas": equipo.notas,
            "costo_total_mensual": res["total_mensual_ars"],
            "costo_total_mensual_usd": res["total_mensual_usd"],
            "costo_unitario_por_test": res["costo_por_test_ars"],
            "costo_unitario_por_test_usd": res["costo_por_test_usd"],
            "created_at": equipo.created_at,
            "updated_at": equipo.updated_at
        }
        return EquipoOut(**data)

    @classmethod
    async def get_all(cls, db: AsyncSession, seccion: Optional[str] = None, activo_only: bool = False) -> List[EquipoOut]:
        query = select(Equipo)
        if seccion:
            query = query.where(Equipo.seccion == seccion)
        if activo_only:
            query = query.where(Equipo.activo == True)
        result = await db.execute(query.order_by(Equipo.nombre))
        equipos = result.scalars().all()
        return [cls._enrich_equipo(eq) for eq in equipos]

    @classmethod
    async def get_by_id(cls, db: AsyncSession, equipo_id: int) -> Optional[EquipoOut]:
        query = select(Equipo).where(Equipo.id == equipo_id)
        result = await db.execute(query)
        eq = result.scalars().first()
        return cls._enrich_equipo(eq) if eq else None

    @classmethod
    async def create(cls, db: AsyncSession, equipo_in: EquipoCreate) -> EquipoOut:
        data = equipo_in.model_dump()
        # Convert consumibles to dict
        if "consumibles_mantenimiento" in data and data["consumibles_mantenimiento"]:
            data["consumibles_mantenimiento"] = [
                c.model_dump() if hasattr(c, "model_dump") else dict(c)
                for c in equipo_in.consumibles_mantenimiento
            ]
        equipo = Equipo(**data)
        db.add(equipo)
        await db.commit()
        await db.refresh(equipo)
        return cls._enrich_equipo(equipo)

    @classmethod
    async def update(cls, db: AsyncSession, equipo_id: int, equipo_in: EquipoUpdate) -> Optional[EquipoOut]:
        query = select(Equipo).where(Equipo.id == equipo_id)
        result = await db.execute(query)
        eq = result.scalars().first()
        if not eq:
            return None

        update_data = equipo_in.model_dump(exclude_unset=True)
        if "consumibles_mantenimiento" in update_data and update_data["consumibles_mantenimiento"] is not None:
            update_data["consumibles_mantenimiento"] = [
                c.model_dump() if hasattr(c, "model_dump") else dict(c)
                for c in update_data["consumibles_mantenimiento"]
            ]

        for k, v in update_data.items():
            setattr(eq, k, v)

        await db.commit()
        await db.refresh(eq)
        return cls._enrich_equipo(eq)

    @classmethod
    async def delete(cls, db: AsyncSession, equipo_id: int) -> bool:
        query = select(Equipo).where(Equipo.id == equipo_id)
        result = await db.execute(query)
        eq = result.scalars().first()
        if not eq:
            return False
        await db.delete(eq)
        await db.commit()
        return True
