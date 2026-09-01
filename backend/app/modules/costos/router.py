from typing import List, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.modules.auth.service import get_current_user
from app.modules.costos.schemas import SimulacionParamsIn, SimulacionResultOut, DashboardResumenOut
from app.modules.costos.calculator_service import CostCalculatorService, round_currency
from app.modules.determinaciones.models import Determinacion
from app.modules.determinaciones.service import DeterminacionService
from app.modules.equipos.models import Equipo
from app.modules.insumos.models import Insumo
from app.modules.costos_generales.models import GastoFijoMensual, ParametroLaboratorio
from app.modules.costos_generales.service import GastosFijosService, ParametrosService

router = APIRouter(prefix="/costos", tags=["Motor de Costos, Simulador y Dashboard"])

@router.post("/simular", response_model=SimulacionResultOut)
async def simular_escenario(
    params: SimulacionParamsIn,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 1. Obtener todas las determinaciones
    dets = await DeterminacionService.get_all(db, activo_only=True)
    dets_dicts = [d.model_dump() for d in dets]
    
    # 2. Gastos fijos y volumen
    gastos_fijos_total = await GastosFijosService.get_total_mensual_activo(db)
    volumen_pacientes = int(await ParametrosService.get_valor_numerico(db, "PACIENTES_MENSUALES_ESTIMADOS", Decimal("1000")))
    
    # 3. Simular
    res = CostCalculatorService.simular_escenario(
        determinaciones_base=dets_dicts,
        variacion_usd_porcentaje=params.variacion_usd_porcentaje,
        variacion_reactivos_porcentaje=params.variacion_reactivos_porcentaje,
        variacion_fijos_porcentaje=params.variacion_fijos_porcentaje,
        variacion_volumen_pacientes_porcentaje=params.variacion_volumen_pacientes_porcentaje,
        gastos_fijos_base=gastos_fijos_total,
        volumen_pacientes_base=volumen_pacientes
    )
    return res

@router.get("/dashboard-resumen", response_model=DashboardResumenOut)
async def get_dashboard_resumen(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Conteos
    count_dets = await db.execute(select(func.count(Determinacion.id)))
    total_dets = count_dets.scalar() or 0
    
    count_eqs = await db.execute(select(func.count(Equipo.id)))
    total_eqs = count_eqs.scalar() or 0
    
    count_ins = await db.execute(select(func.count(Insumo.id)))
    total_ins = count_ins.scalar() or 0
    
    total_fijos = await GastosFijosService.get_total_mensual_activo(db)
    vol_pacientes = int(await ParametrosService.get_valor_numerico(db, "PACIENTES_MENSUALES_ESTIMADOS", Decimal("1000")))
    overhead_prom = round_currency(total_fijos / Decimal(str(max(vol_pacientes, 1))), 2)
    
    # Determinaciones
    dets = await DeterminacionService.get_all(db, activo_only=True)
    dets_dicts = [d.model_dump() for d in dets]
    
    # Top más costosas
    top_mas_costosas = sorted(dets_dicts, key=lambda x: x["costo_unitario_total_ars"], reverse=True)[:5]
    top_costosas_res = [
        {"nombre": d["nombre"], "costo": float(d["costo_unitario_total_ars"]), "seccion": d["seccion"]}
        for d in top_mas_costosas
    ]
    
    # Top menor margen (con arancel > 0)
    con_arancel = [d for d in dets_dicts if d["arancel_referencia_ars"] > 0]
    top_menor_margen = sorted(con_arancel, key=lambda x: x["margen_estimado_porcentaje"])[:5]
    top_margen_res = [
        {"nombre": d["nombre"], "margen_pct": float(d["margen_estimado_porcentaje"]), "costo": float(d["costo_unitario_total_ars"]), "arancel": float(d["arancel_referencia_ars"])}
        for d in top_menor_margen
    ]
    
    # Distribución de gastos fijos por categoría
    gf_all = await GastosFijosService.get_all(db)
    cat_dict = {}
    for g in gf_all:
        if g.activo:
            cat_dict[g.categoria] = cat_dict.get(g.categoria, Decimal("0.0")) + g.monto_mensual
    distribucion_gf = [{"categoria": k, "monto": float(v)} for k, v in cat_dict.items()]
    
    # Costo promedio por sección
    secc_dict = {}
    secc_count = {}
    for d in dets_dicts:
        s = d["seccion"]
        secc_dict[s] = secc_dict.get(s, Decimal("0.0")) + Decimal(str(d["costo_unitario_total_ars"]))
        secc_count[s] = secc_count.get(s, 0) + 1
    costo_prom_secc = [
        {"seccion": k, "costo_promedio": round(float(secc_dict[k] / secc_count[k]), 2), "cantidad": secc_count[k]}
        for k in secc_dict
    ]
    
    return {
        "total_determinaciones": total_dets,
        "total_equipos": total_eqs,
        "total_insumos": total_ins,
        "total_gastos_fijos_mensuales": total_fijos,
        "volumen_pacientes_estimado": vol_pacientes,
        "overhead_promedio_por_paciente": overhead_prom,
        "top_mas_costosas": top_costosas_res,
        "top_menor_margen": top_margen_res,
        "distribucion_gastos_fijos": distribucion_gf,
        "costo_promedio_por_seccion": costo_prom_secc
    }
