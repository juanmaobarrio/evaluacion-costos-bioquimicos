from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field

class SimulacionParamsIn(BaseModel):
    variacion_usd_porcentaje: Decimal = Field(default=Decimal("0.0"), description="Variación % en tipo de cambio USD")
    variacion_reactivos_porcentaje: Decimal = Field(default=Decimal("0.0"), description="Variación % en costo de reactivos")
    variacion_fijos_porcentaje: Decimal = Field(default=Decimal("0.0"), description="Variación % en gastos fijos de estructura")
    variacion_volumen_pacientes_porcentaje: Decimal = Field(default=Decimal("0.0"), description="Variación % en volumen mensual de pacientes")

class DeterminacionSimuladaOut(BaseModel):
    id: int
    codigo: Optional[str]
    nombre: str
    costo_original: Decimal
    costo_simulado: Decimal
    delta_ars: Decimal
    delta_porcentaje: Decimal
    arancel_referencia: Decimal
    nuevo_margen_ars: Decimal
    nuevo_margen_porcentaje: Decimal

class SimulacionResultOut(BaseModel):
    gastos_fijos_simulados: Decimal
    volumen_pacientes_simulado: int
    overhead_por_paciente_simulado: Decimal
    overhead_por_paciente_base: Decimal
    delta_overhead_porcentaje: Decimal
    determinaciones: List[DeterminacionSimuladaOut]

class DashboardResumenOut(BaseModel):
    total_determinaciones: int
    total_equipos: int
    total_insumos: int
    total_gastos_fijos_mensuales: Decimal
    volumen_pacientes_estimado: int
    overhead_promedio_por_paciente: Decimal
    top_mas_costosas: List[Dict[str, Any]]
    top_menor_margen: List[Dict[str, Any]]
    distribucion_gastos_fijos: List[Dict[str, Any]]
    costo_promedio_por_seccion: List[Dict[str, Any]]
