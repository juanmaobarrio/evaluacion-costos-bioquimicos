import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import log
from app.core.database import engine, Base, AsyncSessionLocal

# Import all models so SQLAlchemy mapper registry resolves all relationships
import app.modules.auth.models
import app.modules.equipos.models
import app.modules.insumos.models
import app.modules.determinaciones.models
import app.modules.costos_generales.models
import app.modules.produccion.models
import app.modules.configuracion.models

async def run_auto_migrations():
    """
    Verifica y aplica migraciones automáticas en SQLite / PostgreSQL.
    Si una columna fue agregada a un modelo pero no existe en la base de datos persistida,
    la agrega automáticamente con ALTER TABLE sin perder ningún dato existente.
    """
    async with engine.begin() as conn:
        # 1. Asegurar que todas las tablas existan
        await conn.run_sync(Base.metadata.create_all)

        # 2. Verificar y agregar columnas faltantes en tablas existentes (especialmente SQLite)
        for table_name, table in Base.metadata.tables.items():
            def inspect_and_upgrade(sync_conn):
                inspector = sa.inspect(sync_conn)
                existing_columns = {col["name"] for col in inspector.get_columns(table_name)}

                for column in table.columns:
                    if column.name not in existing_columns:
                        log.info(f"[MIGRACIÓN] Agregando columna faltante '{column.name}' a tabla '{table_name}'...")
                        col_type = column.type.compile(sync_conn.dialect)
                        default_val = "NULL"
                        if column.default is not None:
                            if hasattr(column.default, "arg"):
                                arg = column.default.arg
                                if isinstance(arg, (int, float)):
                                    default_val = str(arg)
                                elif isinstance(arg, str):
                                    default_val = f"'{arg}'"
                                elif isinstance(arg, bool):
                                    default_val = "1" if arg else "0"

                        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type}"
                        try:
                            sync_conn.execute(sa.text(alter_query))
                            log.info(f"[MIGRACIÓN OK] Columna '{column.name}' agregada con éxito.")
                        except Exception as err:
                            log.warning(f"[MIGRACIÓN WARN] No se pudo agregar columna '{column.name}': {err}")

            await conn.run_sync(inspect_and_upgrade)

    # 3. Asegurar que las secciones, tipos de insumo y laboratorios de referencia por defecto existan
    try:
        from app.modules.costos_generales.models import SeccionLaboratorio, ParametroLaboratorio
        from app.modules.configuracion.models import TipoInsumoCatalogo, LaboratorioReferencia
        from sqlalchemy import select, func, text
        from decimal import Decimal
        async with AsyncSessionLocal() as db:
            # Normalizar valores existentes en insumos.tipo a minúsculas (ej: 'REACTIVO' -> 'reactivo')
            try:
                await db.execute(text("UPDATE insumos SET tipo = LOWER(tipo) WHERE tipo != LOWER(tipo)"))
                await db.commit()
            except Exception as e:
                log.debug(f"Normalización insumos.tipo: {e}")

            # Inicializar tipos de insumo por defecto en catálogo
            tipo_count = (await db.execute(select(func.count(TipoInsumoCatalogo.id)))).scalar()
            if not tipo_count or tipo_count == 0:
                log.info("[MIGRACIÓN] Inicializando tipos de insumo por defecto en catálogo...")
                tipos = [
                    TipoInsumoCatalogo(clave="reactivo", nombre="Reactivo Específico", descripcion="Reactivos analíticos, kits de ensayo y sustratos químicos", color="brand", base_calculo_sugerida="test", orden=1),
                    TipoInsumoCatalogo(clave="calibrador", nombre="Calibrador", descripcion="Materiales de calibración multi-analito y específicos", color="purple", base_calculo_sugerida="test", orden=2),
                    TipoInsumoCatalogo(clave="control", nombre="Control de Calidad", descripcion="Sueros y pools control para aseguramiento de calidad analítica", color="amber", base_calculo_sugerida="test", orden=3),
                    TipoInsumoCatalogo(clave="solucion_lavado", nombre="Solución de Lavado", descripcion="Detergentes, diluyentes y soluciones de enjuague de autoanalizador", color="cyan", base_calculo_sugerida="test", orden=4),
                    TipoInsumoCatalogo(clave="descartable_extraccion", nombre="Descartables Extracción", descripcion="Agujas, tubos con anticoagulante, mariposas, algodón, alcohol", color="blue", base_calculo_sugerida="paciente", orden=5),
                    TipoInsumoCatalogo(clave="descartable_equipo", nombre="Descartables Equipo", descripcion="Cubetas de reacción, puntas de pipeta robótica, celdas", color="slate", base_calculo_sugerida="test", orden=6),
                    TipoInsumoCatalogo(clave="otro", nombre="Otro Consumible", descripcion="Materiales misceláneos de laboratorio y bioseguridad", color="slate", base_calculo_sugerida="test", orden=7),
                ]
                db.add_all(tipos)
                await db.commit()
                log.info("[MIGRACIÓN OK] Tipos de insumo iniciales creados.")

            # Inicializar laboratorios de referencia por defecto si no hay ninguno
            lab_count = (await db.execute(select(func.count(LaboratorioReferencia.id)))).scalar()
            if not lab_count or lab_count == 0:
                log.info("[MIGRACIÓN] Inicializando laboratorios de referencia por defecto...")
                labs = [
                    LaboratorioReferencia(nombre="Laboratorio Central de Derivaciones", contacto="Dr. Juan Pérez", telefono="(011) 4567-8900", email="derivaciones@labcentral.com.ar", direccion="Av. Corrientes 1234, CABA", notas="Laboratorio de alta complejidad para pruebas inmunológicas y endocrinas especiales"),
                    LaboratorioReferencia(nombre="Instituto Bioquímico Molecular", contacto="Dra. María González", telefono="(011) 4987-6543", email="contacto@biomolecular.com.ar", direccion="Calle 45 N° 789, La Plata", notas="Especialista en PCR en tiempo real, secuenciación y citogenética"),
                    LaboratorioReferencia(nombre="Centro de Toxicología Especializada", contacto="Dr. Roberto Gómez", telefono="(011) 4321-8765", email="toxicologia@centrolab.com.ar", direccion="San Martín 567, Quilmes", notas="Dosaje de drogas terapéuticas, metales pesados y screening de abuso"),
                ]
                db.add_all(labs)
                await db.commit()
                log.info("[MIGRACIÓN OK] Laboratorios de referencia iniciales creados.")

            sec_count = (await db.execute(select(func.count(SeccionLaboratorio.id)))).scalar()
            if not sec_count or sec_count == 0:
                log.info("[MIGRACIÓN] Inicializando secciones por defecto del laboratorio...")
                secciones = [
                    SeccionLaboratorio(nombre="Química Clínica", descripcion="Pruebas metabólicas, lípidos, enzimas y sustratos", color="emerald"),
                    SeccionLaboratorio(nombre="Hematología y Hemostasia", descripcion="Hemogramas, coagulograma, eritrosedimentación", color="purple"),
                    SeccionLaboratorio(nombre="Inmunología y Serología", descripcion="Inmunoensayos, anticuerpos y pruebas virales", color="sky"),
                    SeccionLaboratorio(nombre="Endocrinología", descripcion="Hormonas tiroideas, fertilidad y marcadores tumorales", color="amber"),
                    SeccionLaboratorio(nombre="Microbiología y Parasitología", descripcion="Urocultivos, hisopados, antibiogramas", color="cyan"),
                    SeccionLaboratorio(nombre="Biología Molecular", descripcion="PCR, carga viral y secuenciación", color="indigo"),
                    SeccionLaboratorio(nombre="Orinas y Medio Interno", descripcion="Sedimento urinario, gases y electrolitos", color="rose"),
                    SeccionLaboratorio(nombre="Toxicología y Monitoreo de Drogas", descripcion="Drogas terapéuticas y de abuso", color="orange"),
                ]
                db.add_all(secciones)
                await db.commit()
                log.info("[MIGRACIÓN OK] Secciones iniciales creadas.")

            # Asegurar parámetros esenciales
            param_count = (await db.execute(select(func.count(ParametroLaboratorio.id)))).scalar()
            if not param_count or param_count == 0:
                log.info("[MIGRACIÓN] Inicializando parámetros de laboratorio por defecto...")
                params = [
                    ParametroLaboratorio(clave="PACIENTES_MENSUALES_ESTIMADOS", valor_numerico=Decimal("1500"), descripcion="Volumen mensual promedio de pacientes atendidos", categoria="Produccion"),
                    ParametroLaboratorio(clave="VALOR_HORA_TECNICO", valor_numerico=Decimal("4500.00"), descripcion="Costo hora mano de obra técnica (ARS)", categoria="ManoDeObra"),
                    ParametroLaboratorio(clave="VALOR_HORA_BIOQUIMICO", valor_numerico=Decimal("9000.00"), descripcion="Costo hora bioquímica de firma y validación (ARS)", categoria="ManoDeObra"),
                    ParametroLaboratorio(clave="USD_EXCHANGE_RATE", valor_numerico=Decimal("1200.00"), descripcion="Tipo de cambio de referencia USD a ARS", categoria="Moneda"),
                ]
                db.add_all(params)
                await db.commit()
                log.info("[MIGRACIÓN OK] Parámetros iniciales creados.")
    except Exception as e:
        log.warning(f"[MIGRACIÓN WARN] Verificación de secciones/parámetros: {e}")
