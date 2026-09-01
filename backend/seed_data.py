import asyncio
from decimal import Decimal
from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import get_password_hash
from app.modules.auth.models import User, UserRole
from app.modules.equipos.models import Equipo, MonedaEquipo
from app.modules.insumos.models import Insumo, TipoInsumo, BaseCalculoInsumo, Moneda
from app.modules.determinaciones.models import Determinacion, DeterminacionInsumo
from app.modules.costos_generales.models import (
    GastoFijoMensual, ParametroLaboratorio, MaterialExtraccionItem, Protocolo, ProtocoloEstudio
)
from app.modules.determinaciones.service import DeterminacionService

async def seed(drop_existing: bool = False):
    async with engine.begin() as conn:
        if drop_existing:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        print("[INFO] Creando usuarios iniciales...")
        admin = User(
            email="admin@laboratorio.com",
            full_name="Administrador General",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        bio = User(
            email="bioquimico@laboratorio.com",
            full_name="Dr. Lucas Perez (Bioquímico Jefe)",
            hashed_password=get_password_hash("bio123"),
            role=UserRole.BIOQUIMICO,
            is_active=True
        )
        db.add_all([admin, bio])
        await db.flush()

        print("[INFO] Creando parámetros del laboratorio...")
        params = [
            ParametroLaboratorio(clave="PACIENTES_MENSUALES_ESTIMADOS", valor_numerico=Decimal("1500"), descripcion="Volumen mensual promedio de pacientes atendidos", categoria="Produccion"),
            ParametroLaboratorio(clave="VALOR_HORA_TECNICO", valor_numerico=Decimal("4500.00"), descripcion="Costo hora mano de obra técnica (ARS)", categoria="ManoDeObra"),
            ParametroLaboratorio(clave="VALOR_HORA_BIOQUIMICO", valor_numerico=Decimal("9000.00"), descripcion="Costo hora bioquímica de firma y validación (ARS)", categoria="ManoDeObra"),
            ParametroLaboratorio(clave="USD_EXCHANGE_RATE", valor_numerico=Decimal("1200.00"), descripcion="Tipo de cambio de referencia USD a ARS", categoria="Moneda"),
        ]
        db.add_all(params)
        await db.flush()

        print("[INFO] Creando gastos fijos mensuales (Overhead)...")
        gastos = [
            GastoFijoMensual(concepto="Alquiler Sede Central y Boxes", categoria="Alquileres", monto_mensual=Decimal("1200000.00")),
            GastoFijoMensual(concepto="Sueldos Personal Administrativo y Recepción", categoria="Sueldos", monto_mensual=Decimal("1800000.00")),
            GastoFijoMensual(concepto="Sueldo Maestranza y Limpieza", categoria="Sueldos", monto_mensual=Decimal("650000.00")),
            GastoFijoMensual(concepto="Servicios Eléctricos (Edenor/Edesur)", categoria="Servicios", monto_mensual=Decimal("380000.00")),
            GastoFijoMensual(concepto="Gas, Agua y Telefonía/Internet", categoria="Servicios", monto_mensual=Decimal("150000.00")),
            GastoFijoMensual(concepto="Licencia Software LIS de Gestión", categoria="Software", monto_mensual=Decimal("160000.00")),
            GastoFijoMensual(concepto="Servicio de Retiro Residuos Patogénicos", categoria="Servicios", monto_mensual=Decimal("140000.00")),
        ]
        db.add_all(gastos)
        await db.flush()

        print("[INFO] Creando autoanalizadores y equipos...")
        eq_cobas = Equipo(
            nombre="Cobas c311",
            marca="Roche Diagnostics",
            modelo="c311",
            seccion="Química Clínica",
            moneda=MonedaEquipo.USD,
            tipo_cambio_al_costear=Decimal("1200.00"),
            costo_alquiler_mensual=Decimal("350.00"),
            costo_mantenimiento_mensual=Decimal("150.00"),
            costo_amortizacion_mensual=Decimal("0.00"),
            costo_calibracion_controles_mensual=Decimal("50.00"),
            volumen_mensual_estimado=4500,
            consumibles_mantenimiento=[],
            activo=True
        )
        eq_sysmex = Equipo(
            nombre="Sysmex XN-550",
            marca="Sysmex",
            modelo="XN-550",
            seccion="Hematología",
            moneda=MonedaEquipo.USD,
            tipo_cambio_al_costear=Decimal("1200.00"),
            costo_alquiler_mensual=Decimal("300.00"),
            costo_mantenimiento_mensual=Decimal("120.00"),
            costo_amortizacion_mensual=Decimal("0.00"),
            costo_calibracion_controles_mensual=Decimal("40.00"),
            volumen_mensual_estimado=2200,
            consumibles_mantenimiento=[],
            activo=True
        )
        eq_architect = Equipo(
            nombre="Architect i1000SR",
            marca="Abbott",
            modelo="i1000SR",
            seccion="Inmunología",
            moneda=MonedaEquipo.USD,
            tipo_cambio_al_costear=Decimal("1200.00"),
            costo_alquiler_mensual=Decimal("500.00"),
            costo_mantenimiento_mensual=Decimal("200.00"),
            costo_amortizacion_mensual=Decimal("0.00"),
            costo_calibracion_controles_mensual=Decimal("100.00"),
            volumen_mensual_estimado=1800,
            consumibles_mantenimiento=[],
            activo=True
        )
        db.add_all([eq_cobas, eq_sysmex, eq_architect])
        await db.flush()

        print("[INFO] Creando insumos y reactivos...")
        # Descartables extracción (Base: Paciente)
        tubo_gel = Insumo(
            codigo="DESC-001",
            nombre="Tubo BD Vacutainer Gel Separador 5ml",
            marca_proveedor="Becton Dickinson",
            tipo=TipoInsumo.DESCARTABLE_EXTRACCION,
            base_calculo=BaseCalculoInsumo.PACIENTE,
            presentacion="Caja x 100 tubos",
            cantidad_por_presentacion=Decimal("100"),
            unidad_medida="unidad",
            costo_presentacion=Decimal("18000.00"),
            moneda=Moneda.ARS,
            tipo_cambio_al_costear=Decimal("1.0"),
            unidades_compradas_periodo=Decimal("15.0"),
            determinaciones_periodo=Decimal("1500.0"),
            costo_por_determinacion_usd=Decimal("18000.0") * Decimal("15.0") / Decimal("1500.0") / Decimal("1200.0"),
            costo_unitario_ars=Decimal("180.00"),
            merma_estimada_porcentaje=Decimal("1.0")
        )
        tubo_edta = Insumo(
            codigo="DESC-002",
            nombre="Tubo BD Vacutainer EDTA K2 3ml",
            marca_proveedor="Becton Dickinson",
            tipo=TipoInsumo.DESCARTABLE_EXTRACCION,
            base_calculo=BaseCalculoInsumo.PACIENTE,
            presentacion="Caja x 100 tubos",
            cantidad_por_presentacion=Decimal("100"),
            unidad_medida="unidad",
            costo_presentacion=Decimal("15000.00"),
            moneda=Moneda.ARS,
            tipo_cambio_al_costear=Decimal("1.0"),
            unidades_compradas_periodo=Decimal("15.0"),
            determinaciones_periodo=Decimal("1500.0"),
            costo_por_determinacion_usd=Decimal("15000.0") * Decimal("15.0") / Decimal("1500.0") / Decimal("1200.0"),
            costo_unitario_ars=Decimal("150.00"),
            merma_estimada_porcentaje=Decimal("1.0")
        )
        aguja_21g = Insumo(
            codigo="DESC-003",
            nombre="Aguja Múltiple BD Vacutainer 21G",
            marca_proveedor="Becton Dickinson",
            tipo=TipoInsumo.DESCARTABLE_EXTRACCION,
            base_calculo=BaseCalculoInsumo.PACIENTE,
            presentacion="Caja x 100 unidades",
            cantidad_por_presentacion=Decimal("100"),
            unidad_medida="unidad",
            costo_presentacion=Decimal("9500.00"),
            moneda=Moneda.ARS,
            tipo_cambio_al_costear=Decimal("1.0"),
            unidades_compradas_periodo=Decimal("15.0"),
            determinaciones_periodo=Decimal("1500.0"),
            costo_por_determinacion_usd=Decimal("9500.0") * Decimal("15.0") / Decimal("1500.0") / Decimal("1200.0"),
            costo_unitario_ars=Decimal("95.00"),
            merma_estimada_porcentaje=Decimal("1.0")
        )
        kit_higiene = Insumo(
            codigo="DESC-004",
            nombre="Algodón, Alcohol 70% y Apósito Adhesivo",
            marca_proveedor="Genérico Farmacia",
            tipo=TipoInsumo.DESCARTABLE_EXTRACCION,
            base_calculo=BaseCalculoInsumo.PACIENTE,
            presentacion="Pack 100 extracciones",
            cantidad_por_presentacion=Decimal("100"),
            unidad_medida="extraccion",
            costo_presentacion=Decimal("4500.00"),
            moneda=Moneda.ARS,
            tipo_cambio_al_costear=Decimal("1.0"),
            unidades_compradas_periodo=Decimal("15.0"),
            determinaciones_periodo=Decimal("1500.0"),
            costo_por_determinacion_usd=Decimal("4500.0") * Decimal("15.0") / Decimal("1500.0") / Decimal("1200.0"),
            costo_unitario_ars=Decimal("45.00"),
            merma_estimada_porcentaje=Decimal("0.0")
        )

        # Reactivos Química
        r_glucosa = Insumo(
            codigo="REA-QUI-001",
            nombre="Glucosa Enzimática Líquida AA",
            marca_proveedor="Wiener Lab / Roche",
            tipo=TipoInsumo.REACTIVO,
            presentacion="Kit 4 x 50 ml (400 determinaciones)",
            cantidad_por_presentacion=Decimal("400"),
            unidad_medida="test",
            costo_presentacion=Decimal("34000.00"),
            moneda=Moneda.ARS,
            tipo_cambio_al_costear=Decimal("1.0"),
            costo_unitario_ars=Decimal("85.00"),
            merma_estimada_porcentaje=Decimal("3.0")
        )
        r_urea = Insumo(
            codigo="REA-QUI-002",
            nombre="Urea Cinética UV",
            marca_proveedor="Wiener Lab",
            tipo=TipoInsumo.REACTIVO,
            presentacion="Kit 250 determinaciones",
            cantidad_por_presentacion=Decimal("250"),
            unidad_medida="test",
            costo_presentacion=Decimal("28750.00"),
            moneda=Moneda.ARS,
            tipo_cambio_al_costear=Decimal("1.0"),
            costo_unitario_ars=Decimal("115.00"),
            merma_estimada_porcentaje=Decimal("2.0")
        )
        r_creatinina = Insumo(
            codigo="REA-QUI-003",
            nombre="Creatinina Cinética Jaffé",
            marca_proveedor="Wiener Lab",
            tipo=TipoInsumo.REACTIVO,
            presentacion="Kit 200 determinaciones",
            cantidad_por_presentacion=Decimal("200"),
            unidad_medida="test",
            costo_presentacion=Decimal("26000.00"),
            moneda=Moneda.ARS,
            tipo_cambio_al_costear=Decimal("1.0"),
            costo_unitario_ars=Decimal("130.00"),
            merma_estimada_porcentaje=Decimal("4.0")
        )
        # Insumos y Reactivos de Alta Precisión (Caso Real Beckman Coulter / AU)
        r_colesterol = Insumo(
            codigo="OSR6216",
            nombre="Reactivo Colesterol Total (OSR6216)",
            marca_proveedor="Beckman Coulter AU",
            tipo=TipoInsumo.REACTIVO,
            presentacion="Kit Reactivo Colesterol",
            cantidad_por_presentacion=Decimal("1"),
            unidad_medida="test",
            costo_presentacion=Decimal("69.20"),
            moneda=Moneda.USD,
            tipo_cambio_al_costear=Decimal("1200.00"),
            unidades_compradas_periodo=Decimal("4.0"),
            determinaciones_periodo=Decimal("31445.0"),
            costo_por_determinacion_usd=Decimal("69.20") * Decimal("4.0") / Decimal("31445.0"),
            costo_unitario_ars=(Decimal("69.20") * Decimal("4.0") / Decimal("31445.0")) * Decimal("1200.00"),
            merma_estimada_porcentaje=Decimal("0.0")
        )
        calibrador_serico = Insumo(
            codigo="BKDR0070-1",
            nombre="Calibrador Sérico 1 (BKDR0070-1)",
            marca_proveedor="Beckman Coulter AU",
            tipo=TipoInsumo.CALIBRADOR,
            presentacion="Vial Calibrador Multi-analito",
            cantidad_por_presentacion=Decimal("1"),
            unidad_medida="test",
            costo_presentacion=Decimal("370.01"),
            moneda=Moneda.USD,
            tipo_cambio_al_costear=Decimal("1200.00"),
            unidades_compradas_periodo=Decimal("1.0"),
            determinaciones_periodo=Decimal("409882.0"),
            costo_por_determinacion_usd=Decimal("370.01") * Decimal("1.0") / Decimal("409882.0"),
            costo_unitario_ars=(Decimal("370.01") * Decimal("1.0") / Decimal("409882.0")) * Decimal("1200.00"),
            merma_estimada_porcentaje=Decimal("0.0")
        )
        control_global = Insumo(
            codigo="BCR3105",
            nombre="Control Global 1 (BCR3105)",
            marca_proveedor="Beckman Coulter AU",
            tipo=TipoInsumo.CONTROL,
            presentacion="Pack Controles de Calidad",
            cantidad_por_presentacion=Decimal("1"),
            unidad_medida="test",
            costo_presentacion=Decimal("50.00"),
            moneda=Moneda.USD,
            tipo_cambio_al_costear=Decimal("1200.00"),
            unidades_compradas_periodo=Decimal("2.0"),
            determinaciones_periodo=Decimal("433843.0"),
            costo_por_determinacion_usd=Decimal("50.00") * Decimal("2.0") / Decimal("433843.0"),
            costo_unitario_ars=(Decimal("50.00") * Decimal("2.0") / Decimal("433843.0")) * Decimal("1200.00"),
            merma_estimada_porcentaje=Decimal("0.0")
        )
        wash_solution = Insumo(
            codigo="OSR0001",
            nombre="Wash Solution AU (OSR0001)",
            marca_proveedor="Beckman Coulter AU",
            tipo=TipoInsumo.SOLUCION_LAVADO,
            presentacion="Bidón Solución Lavado AU",
            cantidad_por_presentacion=Decimal("1"),
            unidad_medida="test",
            costo_presentacion=Decimal("55.65"),
            moneda=Moneda.USD,
            tipo_cambio_al_costear=Decimal("1200.00"),
            unidades_compradas_periodo=Decimal("8.0"),
            determinaciones_periodo=Decimal("433843.0"),
            costo_por_determinacion_usd=Decimal("55.65") * Decimal("8.0") / Decimal("433843.0"),
            costo_unitario_ars=(Decimal("55.65") * Decimal("8.0") / Decimal("433843.0")) * Decimal("1200.00"),
            merma_estimada_porcentaje=Decimal("0.0")
        )

        # Reactivos Hematología
        r_hemograma = Insumo(
            codigo="REA-HEM-001",
            nombre="Pack Reactivos Sysmex XN (Cellpack DCL + Fluorocell)",
            marca_proveedor="Sysmex",
            tipo=TipoInsumo.REACTIVO,
            presentacion="Pack 1000 determinaciones",
            cantidad_por_presentacion=Decimal("1000"),
            unidad_medida="test",
            costo_presentacion=Decimal("280000.00"),
            moneda=Moneda.ARS,
            tipo_cambio_al_costear=Decimal("1.0"),
            costo_unitario_ars=Decimal("280.00"),
            merma_estimada_porcentaje=Decimal("2.0")
        )

        # Reactivos Inmunología (USD)
        r_tsh = Insumo(
            codigo="REA-INM-001",
            nombre="TSH Ultrasensible Alinity/Architect Reagent Kit",
            marca_proveedor="Abbott Laboratories",
            tipo=TipoInsumo.REACTIVO,
            presentacion="Kit x 100 tests",
            cantidad_por_presentacion=Decimal("100"),
            unidad_medida="test",
            costo_presentacion=Decimal("150.00"), # 150 USD
            moneda=Moneda.USD,
            tipo_cambio_al_costear=Decimal("1200.00"),
            costo_unitario_ars=Decimal("1800.00"),
            merma_estimada_porcentaje=Decimal("5.0")
        )

        db.add_all([
            tubo_gel, tubo_edta, aguja_21g, kit_higiene,
            r_glucosa, r_urea, r_creatinina, r_colesterol,
            calibrador_serico, control_global, wash_solution,
            r_hemograma, r_tsh
        ])
        await db.flush()

        print("[INFO] Configurando Kit Estándar de Extracción...")
        mat_ext = [
            MaterialExtraccionItem(insumo_id=tubo_gel.id, cantidad=Decimal("1.0"), es_obligatorio=True),
            MaterialExtraccionItem(insumo_id=aguja_21g.id, cantidad=Decimal("1.0"), es_obligatorio=True),
            MaterialExtraccionItem(insumo_id=kit_higiene.id, cantidad=Decimal("1.0"), es_obligatorio=True)
        ]
        db.add_all(mat_ext)
        await db.flush()

        print("[INFO] Creando determinaciones bioquímicas y asignando insumos...")
        # Glucemia
        det_glucemia = Determinacion(
            codigo="DET-001",
            codigo_nomenclador="0475",
            nombre="Glucemia Cuantitativa",
            seccion="Química Clínica",
            equipo_id=eq_cobas.id,
            tiempo_proceso_minutos=Decimal("2.0"),
            tasa_repeticion_porcentaje=Decimal("4.0"),
            arancel_referencia_ars=Decimal("4500.00"),
            activo=True
        )
        db.add(det_glucemia)
        await db.flush()
        db.add(DeterminacionInsumo(determinacion_id=det_glucemia.id, insumo_id=r_glucosa.id, cantidad_requerida=Decimal("1.0")))

        # Uremia
        det_uremia = Determinacion(
            codigo="DET-002",
            codigo_nomenclador="0901",
            nombre="Uremia",
            seccion="Química Clínica",
            equipo_id=eq_cobas.id,
            tiempo_proceso_minutos=Decimal("2.0"),
            tasa_repeticion_porcentaje=Decimal("3.0"),
            arancel_referencia_ars=Decimal("4200.00"),
            activo=True
        )
        db.add(det_uremia)
        await db.flush()
        db.add(DeterminacionInsumo(determinacion_id=det_uremia.id, insumo_id=r_urea.id, cantidad_requerida=Decimal("1.0")))

        # Creatinina
        det_creatinina = Determinacion(
            codigo="DET-003",
            codigo_nomenclador="0228",
            nombre="Creatininemia",
            seccion="Química Clínica",
            equipo_id=eq_cobas.id,
            tiempo_proceso_minutos=Decimal("2.0"),
            tasa_repeticion_porcentaje=Decimal("4.0"),
            arancel_referencia_ars=Decimal("4800.00"),
            activo=True
        )
        db.add(det_creatinina)
        await db.flush()
        db.add(DeterminacionInsumo(determinacion_id=det_creatinina.id, insumo_id=r_creatinina.id, cantidad_requerida=Decimal("1.0")))

        # Colesterol Total (Caso Real Beckman Coulter / AU)
        det_colesterol = Determinacion(
            codigo="DET-004",
            codigo_nomenclador="0203",
            nombre="Colesterol Total (Beckman AU)",
            seccion="Química Clínica",
            equipo_id=eq_cobas.id,
            tiempo_proceso_minutos=Decimal("0.0"),
            tasa_repeticion_porcentaje=Decimal("0.0"),
            arancel_referencia_ars=Decimal("5200.00"),
            arancel_referencia_usd=Decimal("4.33"),
            activo=True
        )
        db.add(det_colesterol)
        await db.flush()
        # Asignar los 4 insumos y consumibles de la práctica
        db.add(DeterminacionInsumo(determinacion_id=det_colesterol.id, insumo_id=r_colesterol.id, cantidad_requerida=Decimal("1.0")))
        db.add(DeterminacionInsumo(determinacion_id=det_colesterol.id, insumo_id=calibrador_serico.id, cantidad_requerida=Decimal("1.0")))
        db.add(DeterminacionInsumo(determinacion_id=det_colesterol.id, insumo_id=control_global.id, cantidad_requerida=Decimal("1.0")))
        db.add(DeterminacionInsumo(determinacion_id=det_colesterol.id, insumo_id=wash_solution.id, cantidad_requerida=Decimal("1.0")))

        # Hemograma Completo
        det_hemo = Determinacion(
            codigo="DET-005",
            codigo_nomenclador="0475",
            nombre="Hemograma Automatizado Completo con Fórmula",
            seccion="Hematología",
            equipo_id=eq_sysmex.id,
            tiempo_proceso_minutos=Decimal("3.0"),
            tasa_repeticion_porcentaje=Decimal("5.0"),
            arancel_referencia_ars=Decimal("6800.00"),
            activo=True
        )
        db.add(det_hemo)
        await db.flush()
        db.add(DeterminacionInsumo(determinacion_id=det_hemo.id, insumo_id=r_hemograma.id, cantidad_requerida=Decimal("1.0")))

        # TSH
        det_tsh = Determinacion(
            codigo="DET-006",
            codigo_nomenclador="0850",
            nombre="TSH Tirotrofina Ultrasensible",
            seccion="Inmunología",
            equipo_id=eq_architect.id,
            tiempo_proceso_minutos=Decimal("4.0"),
            tasa_repeticion_porcentaje=Decimal("6.0"),
            arancel_referencia_ars=Decimal("18500.00"),
            activo=True
        )
        db.add(det_tsh)
        await db.flush()
        db.add(DeterminacionInsumo(determinacion_id=det_tsh.id, insumo_id=r_tsh.id, cantidad_requerida=Decimal("1.0")))

        await db.commit()

        # Recalcular costos unitarios con el servicio oficial
        print("[INFO] Recalculando matrices de costo de determinaciones...")
        await DeterminacionService.recalcular_todas(db)

        # Crear Protocolo / Rutina
        print("[INFO] Creando protocolo de Chequeo General...")
        proto_rutina = Protocolo(
            nombre="Chequeo Básico Preventivo",
            codigo="PROT-001",
            descripcion="Incluye Hemograma, Glucemia, Uremia, Creatinina y Colesterol",
            arancel_sugerido_ars=Decimal("26000.00"),
            activo=True
        )
        db.add(proto_rutina)
        await db.flush()

        for d in [det_hemo, det_glucemia, det_uremia, det_creatinina, det_colesterol]:
            db.add(ProtocoloEstudio(protocolo_id=proto_rutina.id, determinacion_id=d.id))

        await db.commit()
        print("[OK] Base de datos inicializada y poblada con éxito!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
