from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.core.config import settings
from app.modules.insumos.models import Insumo, TipoInsumo, Moneda
from app.modules.insumos.schemas import InsumoCreate, InsumoUpdate, InsumoOut
from app.modules.costos.calculator_service import CostCalculatorService

class InsumoService:
    @staticmethod
    def _calcular_costo_unitario(insumo_data: dict) -> dict:
        moneda = insumo_data.get("moneda", Moneda.USD)
        costo_pres = Decimal(str(insumo_data.get("costo_presentacion", 0)))
        unidades = Decimal(str(insumo_data.get("unidades_compradas_periodo", 1)))
        det_periodo = Decimal(str(insumo_data.get("determinaciones_periodo", 1)))

        # Si determinaciones_periodo no fue especificado o es 1 pero tiene cantidad_por_presentacion > 1
        cant_pres = Decimal(str(insumo_data.get("cantidad_por_presentacion", 1)))
        if det_periodo <= Decimal("1.0") and cant_pres > Decimal("1.0"):
            det_periodo = cant_pres

        tc = Decimal(str(insumo_data.get("tipo_cambio_al_costear", settings.USD_EXCHANGE_RATE)))
        merma = Decimal(str(insumo_data.get("merma_estimada_porcentaje", 0)))

        return CostCalculatorService.calcular_costo_unitario_insumo_exacto(
            costo_compra=costo_pres,
            unidades_compradas_periodo=unidades,
            determinaciones_periodo=det_periodo,
            moneda=moneda.value if hasattr(moneda, "value") else str(moneda),
            tipo_cambio_usd=tc,
            merma_porcentaje=merma
        )

    @classmethod
    async def get_all(
        cls,
        db: AsyncSession,
        tipo: Optional[str] = None,
        search: Optional[str] = None,
        activo_only: bool = False
    ) -> List[Insumo]:
        query = select(Insumo)
        if tipo:
            query = query.where(Insumo.tipo == tipo.lower().strip())
        if activo_only:
            query = query.where(Insumo.activo == True)
        if search:
            query = query.where(
                (Insumo.nombre.ilike(f"%{search}%")) |
                (Insumo.codigo.ilike(f"%{search}%")) |
                (Insumo.marca_proveedor.ilike(f"%{search}%"))
            )
        result = await db.execute(query.order_by(Insumo.nombre))
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, insumo_id: int) -> Optional[Insumo]:
        query = select(Insumo).where(Insumo.id == insumo_id)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def create(cls, db: AsyncSession, insumo_in: InsumoCreate) -> Insumo:
        data = insumo_in.model_dump()
        if "tipo" in data and data["tipo"]:
            data["tipo"] = data["tipo"].lower().strip()
        calc = cls._calcular_costo_unitario(data)
        data["costo_por_determinacion_usd"] = calc["costo_por_determinacion_usd"]
        data["costo_unitario_ars"] = calc["costo_unitario_ars"]
        insumo = Insumo(**data)
        db.add(insumo)
        await db.commit()
        await db.refresh(insumo)
        return insumo

    @classmethod
    async def update(cls, db: AsyncSession, insumo_id: int, insumo_in: InsumoUpdate) -> Optional[Insumo]:
        insumo = await cls.get_by_id(db, insumo_id)
        if not insumo:
            return None

        update_data = insumo_in.model_dump(exclude_unset=True)
        if "tipo" in update_data and update_data["tipo"]:
            update_data["tipo"] = update_data["tipo"].lower().strip()
        # Combinar datos existentes con actualizados para recalcular costo_unitario
        merged = {
            "moneda": update_data.get("moneda", insumo.moneda),
            "costo_presentacion": update_data.get("costo_presentacion", insumo.costo_presentacion),
            "cantidad_por_presentacion": update_data.get("cantidad_por_presentacion", insumo.cantidad_por_presentacion),
            "unidades_compradas_periodo": update_data.get("unidades_compradas_periodo", insumo.unidades_compradas_periodo),
            "determinaciones_periodo": update_data.get("determinaciones_periodo", insumo.determinaciones_periodo),
            "tipo_cambio_al_costear": update_data.get("tipo_cambio_al_costear", insumo.tipo_cambio_al_costear),
            "merma_estimada_porcentaje": update_data.get("merma_estimada_porcentaje", insumo.merma_estimada_porcentaje),
        }
        calc = cls._calcular_costo_unitario(merged)
        update_data["costo_por_determinacion_usd"] = calc["costo_por_determinacion_usd"]
        update_data["costo_unitario_ars"] = calc["costo_unitario_ars"]

        for k, v in update_data.items():
            setattr(insumo, k, v)

        await db.commit()
        await db.refresh(insumo)
        return insumo

    @classmethod
    async def delete(cls, db: AsyncSession, insumo_id: int) -> bool:
        insumo = await cls.get_by_id(db, insumo_id)
        if not insumo:
            return False
        await db.delete(insumo)
        await db.commit()
        return True
