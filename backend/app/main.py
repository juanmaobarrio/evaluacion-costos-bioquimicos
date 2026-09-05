from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, log
from app.core.database import engine, Base

# Import all models so Base metadata is completely populated
import app.modules.auth.models
import app.modules.equipos.models
import app.modules.insumos.models
import app.modules.determinaciones.models
import app.modules.costos_generales.models
import app.modules.produccion.models
import app.modules.configuracion.models

# Routers
from app.modules.auth.router import router as auth_router
from app.modules.equipos.router import router as equipos_router
from app.modules.insumos.router import router as insumos_router
from app.modules.determinaciones.router import router as determinaciones_router
from app.modules.costos_generales.router import router as costos_generales_router
from app.modules.costos.router import router as costos_router
from app.modules.produccion.router import router as produccion_router
from app.modules.configuracion.router import router as configuracion_router

from app.core.migration import run_auto_migrations

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    log.info("Iniciando Sistema de Costos Bioquímicos...")

    # 1. Ejecutar migraciones automáticas de esquema (agrega tablas y columnas faltantes)
    try:
        await run_auto_migrations()
        log.info("Migraciones de base de datos verificadas y aplicadas.")
    except Exception as e:
        log.error(f"Error en migraciones automáticas: {e}")

    # 2. Auto-seed si la base de datos es nueva (primer despliegue en Docker / ZimaBoard)
    try:
        from app.core.database import AsyncSessionLocal
        from app.modules.auth.models import User
        from sqlalchemy import select, func
        async with AsyncSessionLocal() as db:
            user_count = (await db.execute(select(func.count(User.id)))).scalar()
            if not user_count or user_count == 0:
                log.info("Base de datos nueva detectada. Poblando datos iniciales...")
                from seed_data import seed
                await seed()
                log.info("Datos iniciales cargados con éxito.")
    except Exception as e:
        log.warning(f"Aviso en verificación de datos iniciales: {e}")

    yield
    log.info("Apagando aplicación.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(equipos_router, prefix=settings.API_V1_STR)
app.include_router(insumos_router, prefix=settings.API_V1_STR)
app.include_router(determinaciones_router, prefix=settings.API_V1_STR)
app.include_router(costos_generales_router, prefix=settings.API_V1_STR)
app.include_router(costos_router, prefix=settings.API_V1_STR)
app.include_router(produccion_router, prefix=settings.API_V1_STR)
app.include_router(configuracion_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "sistema": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
        "status": "online"
    }
