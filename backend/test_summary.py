import asyncio
import httpx
from decimal import Decimal
from app.core.database import AsyncSessionLocal, engine
from app.modules.determinaciones.service import DeterminacionService
from app.modules.equipos.service import EquipoService
from app.modules.costos_generales.service import ProtocoloService, GastosFijosService

async def test_summary():
    async with AsyncSessionLocal() as db:
        equipos = await EquipoService.get_all(db)
        print(f"\n--- EQUIPOS REGISTRADOS ({len(equipos)}) ---")
        for eq in equipos:
            print(f"- {eq.nombre} ({eq.seccion}): Gasto Mensual = ${eq.costo_total_mensual:,.2f} | Costo/Test = ${eq.costo_unitario_por_test:,.4f}")

        dets = await DeterminacionService.get_all(db)
        print(f"\n--- DETERMINACIONES ({len(dets)}) ---")
        for d in dets:
            print(f"- [{d.codigo}] {d.nombre}: Costo Total = ${d.costo_unitario_total_ars:,.4f} | Arancel = ${d.arancel_referencia_ars:,.2f} | Margen = {d.margen_estimado_porcentaje}%")

        protos = await ProtocoloService.get_all(db)
        print(f"\n--- PROTOCOLOS / CHEQUEOS ({len(protos)}) ---")
        for p in protos:
            print(f"- [{p.codigo}] {p.nombre}: Costo Total Paciente = ${p.costo_total_protocolo_ars:,.2f} | Arancel = ${p.arancel_sugerido_ars:,.2f} | Margen = {p.margen_estimado_porcentaje}%")

        gf = await GastosFijosService.get_total_mensual_activo(db)
        print(f"\n--- GASTOS FIJOS TOTALES ACTIVOS: ${gf:,.2f} ---")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_summary())
