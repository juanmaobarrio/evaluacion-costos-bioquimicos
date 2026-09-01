from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional

def round_currency(value: Decimal, places: int = 4) -> Decimal:
    """Redondeo de alta precisión para costos unitarios."""
    if value is None:
        return Decimal("0.0000")
    fmt = Decimal("10") ** -places
    return Decimal(str(value)).quantize(fmt, rounding=ROUND_HALF_UP)

class CostCalculatorService:
    @staticmethod
    def calcular_costo_unitario_insumo_exacto(
        costo_compra: Decimal,
        unidades_compradas_periodo: Decimal,
        determinaciones_periodo: Decimal,
        moneda: str,
        tipo_cambio_usd: Decimal = Decimal("1200.0"),
        merma_porcentaje: Decimal = Decimal("0.0")
    ) -> Dict[str, Decimal]:
        """
        Calcula el costo por determinación de un insumo/consumible/calibrador/lavador
        utilizando la fórmula exacta: (costo_compra * unidades_compradas) / determinaciones_periodo.
        """
        if determinaciones_periodo is None or determinaciones_periodo <= Decimal("0"):
            return {
                "costo_por_determinacion_usd": Decimal("0.000000"),
                "costo_unitario_ars": Decimal("0.000000")
            }

        unidades = unidades_compradas_periodo if (unidades_compradas_periodo and unidades_compradas_periodo > Decimal("0")) else Decimal("1.0")

        if moneda.upper() == "USD":
            costo_usd = (costo_compra * unidades) / determinaciones_periodo
            costo_ars = costo_usd * tipo_cambio_usd
        else:
            costo_ars = (costo_compra * unidades) / determinaciones_periodo
            costo_usd = costo_ars / tipo_cambio_usd if tipo_cambio_usd > Decimal("0") else Decimal("0.0")

        if merma_porcentaje and merma_porcentaje > Decimal("0"):
            factor_merma = Decimal("1.0") + (merma_porcentaje / Decimal("100.0"))
            costo_usd = costo_usd * factor_merma
            costo_ars = costo_ars * factor_merma

        return {
            "costo_por_determinacion_usd": round_currency(costo_usd, 6),
            "costo_unitario_ars": round_currency(costo_ars, 6)
        }

    @staticmethod
    def calcular_costo_unitario_insumo(
        costo_presentacion: Decimal,
        cantidad_por_presentacion: Decimal,
        moneda: str,
        tipo_cambio_usd: Decimal = Decimal("1.0"),
        merma_porcentaje: Decimal = Decimal("0.0")
    ) -> Decimal:
        """
        Calcula el costo unitario en ARS de un insumo considerando tipo de cambio y factor de merma.
        """
        if cantidad_por_presentacion <= Decimal("0"):
            return Decimal("0.0000")

        costo_ars = costo_presentacion
        if moneda.upper() == "USD":
            costo_ars = costo_presentacion * tipo_cambio_usd

        costo_base_unidad = costo_ars / cantidad_por_presentacion

        # Aplicar factor de merma si existe
        if merma_porcentaje > Decimal("0"):
            factor_merma = Decimal("1.0") + (merma_porcentaje / Decimal("100.0"))
            costo_base_unidad = costo_base_unidad * factor_merma

        return round_currency(costo_base_unidad, 4)

    @staticmethod
    def calcular_costos_equipo(
        costo_alquiler: Decimal,
        costo_mantenimiento: Decimal,
        costo_amortizacion: Decimal,
        costo_calibracion_controles: Decimal,
        consumibles_mantenimiento: List[Dict[str, Any]],
        volumen_mensual: int,
        moneda: str = "ARS",
        tipo_cambio_usd: Decimal = Decimal("1200.0")
    ) -> Dict[str, Decimal]:
        """
        Calcula el costo fijo mensual total del equipo (en USD y ARS) y su prorrateo unitario por test.
        """
        tc = tipo_cambio_usd if (tipo_cambio_usd and tipo_cambio_usd > Decimal("0")) else Decimal("1200.0")

        consumibles_total = Decimal("0.0")
        if consumibles_mantenimiento:
            for item in consumibles_mantenimiento:
                monto = item.get("costo_mensual", 0) if isinstance(item, dict) else getattr(item, "costo_mensual", 0)
                consumibles_total += Decimal(str(monto or 0))

        subtotal_base = (
            Decimal(str(costo_alquiler or 0)) +
            Decimal(str(costo_mantenimiento or 0)) +
            Decimal(str(costo_amortizacion or 0)) +
            Decimal(str(costo_calibracion_controles or 0)) +
            consumibles_total
        )

        if str(moneda).upper() == "USD":
            total_usd = subtotal_base
            total_ars = subtotal_base * tc
        else:
            total_ars = subtotal_base
            total_usd = subtotal_base / tc

        volumen = max(volumen_mensual, 1)
        costo_por_test_ars = total_ars / Decimal(str(volumen))
        costo_por_test_usd = total_usd / Decimal(str(volumen))

        return {
            "total_mensual": round_currency(total_ars, 2),
            "total_mensual_ars": round_currency(total_ars, 2),
            "total_mensual_usd": round_currency(total_usd, 2),
            "consumibles_total": round_currency(consumibles_total, 2),
            "costo_por_test": round_currency(costo_por_test_ars, 4),
            "costo_por_test_ars": round_currency(costo_por_test_ars, 4),
            "costo_por_test_usd": round_currency(costo_por_test_usd, 6)
        }

    @staticmethod
    def calcular_costo_determinacion(
        insumos_con_cantidad: List[Dict[str, Any]], # [{"costo_unitario_ars": Decimal, "costo_por_determinacion_usd": Decimal, "cantidad": Decimal}]
        costo_equipo_por_test: Decimal = Decimal("0.0"),
        tasa_repeticion_porcentaje: Decimal = Decimal("0.0"),
        tiempo_proceso_minutos: Decimal = Decimal("0.0"),
        costo_hora_mano_obra: Decimal = Decimal("0.0"),
        tipo_cambio_usd: Decimal = Decimal("1200.0")
    ) -> Dict[str, Decimal]:
        """
        Calcula el costo total y desglosado de una determinación bioquímica (en ARS y USD).
        """
        costo_reactivos_ars = Decimal("0.0")
        costo_reactivos_usd = Decimal("0.0")

        for item in insumos_con_cantidad:
            costo_ars = Decimal(str(item.get("costo_unitario_ars", 0)))
            costo_usd = Decimal(str(item.get("costo_por_determinacion_usd", 0)))
            cant = Decimal(str(item.get("cantidad", 1)))

            costo_reactivos_ars += costo_ars * cant
            costo_reactivos_usd += costo_usd * cant

        # Mano de obra proporcional
        costo_mano_obra_ars = Decimal("0.0")
        if tiempo_proceso_minutos and costo_hora_mano_obra:
            costo_mano_obra_ars = (Decimal(str(tiempo_proceso_minutos)) / Decimal("60.0")) * Decimal(str(costo_hora_mano_obra))

        costo_mano_obra_usd = costo_mano_obra_ars / tipo_cambio_usd if tipo_cambio_usd > Decimal("0") else Decimal("0.0")

        costo_equipo_ars = Decimal(str(costo_equipo_por_test or 0))
        costo_equipo_usd = costo_equipo_ars / tipo_cambio_usd if tipo_cambio_usd > Decimal("0") else Decimal("0.0")

        costo_total_ars = costo_reactivos_ars + costo_equipo_ars + costo_mano_obra_ars
        costo_total_usd = costo_reactivos_usd + costo_equipo_usd + costo_mano_obra_usd

        return {
            "costo_reactivos_puro": round_currency(costo_reactivos_ars, 4),
            "costo_reactivos_usd": round_currency(costo_reactivos_usd, 6),
            "costo_reactivos_con_repeticion": round_currency(costo_reactivos_ars, 4),
            "costo_repeticion_incremental": Decimal("0.0000"),
            "costo_equipo": round_currency(costo_equipo_ars, 4),
            "costo_equipo_usd": round_currency(costo_equipo_usd, 6),
            "costo_mano_obra": round_currency(costo_mano_obra_ars, 4),
            "costo_mano_obra_usd": round_currency(costo_mano_obra_usd, 6),
            "costo_unitario_total": round_currency(costo_total_ars, 4),
            "costo_unitario_total_usd": round_currency(costo_total_usd, 6)
        }

    @staticmethod
    def calcular_costo_protocolo(
        costo_total_estudios: Decimal,
        costo_extraccion_descartables: Decimal,
        total_gastos_fijos_mensuales: Decimal,
        volumen_pacientes_mensual: int
    ) -> Dict[str, Decimal]:
        """
        Calcula el costo completo por paciente o protocolo (orden médica) con absorción de gastos fijos.
        """
        volumen = max(volumen_pacientes_mensual, 1)
        overhead_por_paciente = Decimal(str(total_gastos_fijos_mensuales or 0)) / Decimal(str(volumen))

        total_protocolo = (
            Decimal(str(costo_total_estudios or 0)) +
            Decimal(str(costo_extraccion_descartables or 0)) +
            overhead_por_paciente
        )

        return {
            "costo_estudios": round_currency(Decimal(str(costo_total_estudios or 0)), 2),
            "costo_extraccion": round_currency(Decimal(str(costo_extraccion_descartables or 0)), 2),
            "overhead_por_paciente": round_currency(overhead_por_paciente, 2),
            "costo_total_protocolo": round_currency(total_protocolo, 2)
        }

    @staticmethod
    def simular_escenario(
        determinaciones_base: List[Dict[str, Any]],
        variacion_usd_porcentaje: Decimal = Decimal("0.0"),
        variacion_reactivos_porcentaje: Decimal = Decimal("0.0"),
        variacion_fijos_porcentaje: Decimal = Decimal("0.0"),
        variacion_volumen_pacientes_porcentaje: Decimal = Decimal("0.0"),
        gastos_fijos_base: Decimal = Decimal("0.0"),
        volumen_pacientes_base: int = 1000
    ) -> Dict[str, Any]:
        """
        Simulador What-If de escenarios de sensibilidad financiera.
        """
        # Calcular nuevo overhead
        factor_fijos = Decimal("1.0") + (variacion_fijos_porcentaje / Decimal("100.0"))
        gastos_fijos_simulados = gastos_fijos_base * factor_fijos

        factor_volumen = Decimal("1.0") + (variacion_volumen_pacientes_porcentaje / Decimal("100.0"))
        volumen_simulado = max(int(Decimal(str(volumen_pacientes_base)) * factor_volumen), 1)

        overhead_unitario_simulado = gastos_fijos_simulados / Decimal(str(volumen_simulado))
        overhead_unitario_base = gastos_fijos_base / Decimal(str(max(volumen_pacientes_base, 1)))

        factor_reactivos = (Decimal("1.0") + (variacion_reactivos_porcentaje / Decimal("100.0"))) * (Decimal("1.0") + (variacion_usd_porcentaje / Decimal("100.0")))

        determinaciones_simuladas = []
        for det in determinaciones_base:
            costo_react_orig = Decimal(str(det.get("costo_reactivos_ars", 0)))
            costo_equipo_orig = Decimal(str(det.get("costo_equipo_ars", 0)))
            costo_mo_orig = Decimal(str(det.get("costo_mano_obra_ars", 0)))

            nuevo_costo_react = round_currency(costo_react_orig * factor_reactivos, 4)
            nuevo_total = round_currency(nuevo_costo_react + costo_equipo_orig + costo_mo_orig, 4)
            costo_original_total = Decimal(str(det.get("costo_unitario_total_ars", 0)))
            delta = nuevo_total - costo_original_total
            delta_pct = (delta / costo_original_total * Decimal("100.0")) if costo_original_total > 0 else Decimal("0.0")

            arancel = Decimal(str(det.get("arancel_referencia_ars", 0)))
            nuevo_margen_ars = arancel - nuevo_total
            nuevo_margen_pct = (nuevo_margen_ars / arancel * Decimal("100.0")) if arancel > 0 else Decimal("0.0")

            determinaciones_simuladas.append({
                "id": det.get("id"),
                "codigo": det.get("codigo"),
                "nombre": det.get("nombre"),
                "costo_original": round_currency(costo_original_total, 2),
                "costo_simulado": round_currency(nuevo_total, 2),
                "delta_ars": round_currency(delta, 2),
                "delta_porcentaje": round_currency(delta_pct, 2),
                "arancel_referencia": round_currency(arancel, 2),
                "nuevo_margen_ars": round_currency(nuevo_margen_ars, 2),
                "nuevo_margen_porcentaje": round_currency(nuevo_margen_pct, 2)
            })

        return {
            "gastos_fijos_simulados": round_currency(gastos_fijos_simulados, 2),
            "volumen_pacientes_simulado": volumen_simulado,
            "overhead_por_paciente_simulado": round_currency(overhead_unitario_simulado, 2),
            "overhead_por_paciente_base": round_currency(overhead_unitario_base, 2),
            "delta_overhead_porcentaje": round_currency(((overhead_unitario_simulado - overhead_unitario_base) / overhead_unitario_base * Decimal("100.0")) if overhead_unitario_base > 0 else Decimal("0.0"), 2),
            "determinaciones": determinaciones_simuladas
        }
