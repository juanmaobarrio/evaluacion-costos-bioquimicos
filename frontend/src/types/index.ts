export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'admin' | 'bioquimico' | 'consulta';
  is_active: boolean;
}

export interface Insumo {
  id: number;
  codigo?: string;
  nombre: string;
  marca_proveedor?: string;
  tipo: 'reactivo' | 'calibrador' | 'control' | 'solucion_lavado' | 'descartable_extraccion' | 'descartable_equipo' | 'otro';
  base_calculo: 'test' | 'paciente';
  presentacion?: string;
  cantidad_por_presentacion: number;
  unidad_medida: string;
  costo_presentacion: number;
  moneda: 'ARS' | 'USD';
  tipo_cambio_al_costear: number;
  unidades_compradas_periodo: number;
  determinaciones_periodo: number;
  costo_por_determinacion_usd: number;
  costo_unitario_ars: number;
  merma_estimada_porcentaje: number;
  activo: boolean;
  notas?: string;
}

export interface ConsumibleMantenimiento {
  nombre: string;
  costo_mensual: number;
  descripcion?: string;
}

export interface Equipo {
  id: number;
  nombre: string;
  marca?: string;
  modelo?: string;
  seccion: string;
  moneda: 'ARS' | 'USD';
  tipo_cambio_al_costear: number;
  costo_alquiler_mensual: number;
  costo_mantenimiento_mensual: number;
  costo_amortizacion_mensual: number;
  costo_calibracion_controles_mensual: number;
  volumen_mensual_estimado: number;
  consumibles_mantenimiento: ConsumibleMantenimiento[];
  costo_total_mensual: number;
  costo_total_mensual_usd?: number;
  costo_unitario_por_test: number;
  costo_unitario_por_test_usd?: number;
  activo: boolean;
  notas?: string;
}

export interface DeterminacionInsumo {
  id: number;
  insumo_id: number;
  cantidad_requerida: number;
  costo_subtotal_ars: number;
  costo_subtotal_usd: number;
  insumo?: Insumo;
}

export interface Determinacion {
  id: number;
  codigo?: string;
  codigo_nomenclador?: string;
  nombre: string;
  seccion: string;
  equipo_id?: number;
  tiempo_proceso_minutos: number;
  tasa_repeticion_porcentaje: number;
  arancel_referencia_ars: number;
  arancel_referencia_usd?: number;
  costo_reactivos_ars: number;
  costo_reactivos_usd?: number;
  costo_equipo_ars: number;
  costo_equipo_usd?: number;
  costo_repeticion_ars: number;
  costo_mano_obra_ars: number;
  costo_mano_obra_usd?: number;
  costo_unitario_total_ars: number;
  costo_unitario_total_usd?: number;
  margen_estimado_porcentaje: number;
  margen_bruto_ars: number;
  margen_bruto_usd?: number;
  equipo?: Equipo;
  insumos_asociados: DeterminacionInsumo[];
  activo: boolean;
  notas?: string;
}

export interface GastoFijo {
  id: number;
  concepto: string;
  categoria: string;
  monto_mensual: number;
  activo: boolean;
  notas?: string;
}

export interface ProtocoloEstudio {
  id: number;
  determinacion_id: number;
  determinacion?: Determinacion;
}

export interface Protocolo {
  id: number;
  nombre: string;
  codigo?: string;
  descripcion?: string;
  costo_determinaciones_ars: number;
  costo_extraccion_descartables_ars: number;
  costo_overhead_fijo_ars: number;
  costo_total_protocolo_ars: number;
  arancel_sugerido_ars: number;
  margen_bruto_ars: number;
  margen_estimado_porcentaje: number;
  estudios: ProtocoloEstudio[];
  activo: boolean;
}

export interface SimulacionParams {
  variacion_usd_porcentaje: number;
  variacion_reactivos_porcentaje: number;
  variacion_fijos_porcentaje: number;
  variacion_volumen_pacientes_porcentaje: number;
}
