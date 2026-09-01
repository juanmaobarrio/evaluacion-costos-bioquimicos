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

    # 3. Asegurar que las secciones por defecto existan
    try:
        from app.modules.costos_generales.models import SeccionLaboratorio
        from sqlalchemy import select, func
        async with AsyncSessionLocal() as db:
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
    except Exception as e:
        log.warning(f"[MIGRACIÓN WARN] Verificación de secciones: {e}")
