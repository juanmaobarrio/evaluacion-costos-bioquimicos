<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight text-white">Catálogo de Determinaciones</h1>
        <p class="text-sm text-slate-400">Modelado analítico de costos unitarios directos e indirectos por práctica bioquímica</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="recalcularTodos" :disabled="recalculando" class="btn-secondary text-xs">
          <i class="pi pi-sync" :class="{ 'pi-spin': recalculando }"></i>
          <span>Recalcular Todo</span>
        </button>
        <button @click="openNewDialog" class="btn-primary text-xs">
          <i class="pi pi-plus"></i>
          <span>Nueva Determinación</span>
        </button>
      </div>
    </div>

    <!-- Filters & Table -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      <div class="flex flex-col sm:flex-row gap-4 justify-between items-center">
        <div class="relative w-full sm:w-80">
          <i class="pi pi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-sm"></i>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por nombre o código..."
            class="form-input !pl-11 text-xs"
          />
        </div>
        <div class="flex items-center gap-2 w-full sm:w-auto">
          <select v-model="selectedSeccion" class="form-input text-xs w-full sm:w-48">
            <option value="">Todas las Secciones</option>
            <option v-for="sec in seccionesList" :key="sec.id" :value="sec.nombre">{{ sec.nombre }}</option>
          </select>
        </div>
      </div>

      <!-- Table -->
      <DataTable
        :value="filteredDeterminaciones"
        :paginator="true"
        :rows="10"
        :loading="loading"
        responsiveLayout="scroll"
        class="text-xs"
      >
        <Column field="codigo" header="Código" style="width: 100px">
          <template #body="{ data }">
            <span class="font-mono text-emerald-400 font-bold">{{ data.codigo || '-' }}</span>
          </template>
        </Column>

        <Column field="nombre" header="Determinación / Estudio" :sortable="true">
          <template #body="{ data }">
            <div class="font-semibold text-slate-100 text-sm">{{ data.nombre }}</div>
            <div class="text-[11px] text-slate-400">{{ data.seccion }}</div>
          </template>
        </Column>

        <Column field="equipo.nombre" header="Equipo" :sortable="true" style="width: 200px">
          <template #body="{ data }">
            <div class="font-medium text-slate-200 flex items-center gap-1.5">
              <i class="pi pi-server text-emerald-400 text-xs"></i>
              <span>{{ data.equipo?.nombre || 'Manual / Sin Equipo' }}</span>
            </div>
            <div v-if="data.equipo" class="text-[10px] text-slate-500 font-mono">
              ${{ formatCurrency(data.costo_equipo_ars) }}/test prorrateado
            </div>
          </template>
        </Column>

        <Column field="costo_unitario_total_ars" header="Costo Total" :sortable="true" style="width: 180px">
          <template #body="{ data }">
            <div class="font-bold text-rose-400 font-mono text-sm">
              USD ${{ formatHighPrecision(data.costo_unitario_total_usd) }}
            </div>
            <div class="text-[10px] text-slate-400 font-mono">
              ARS ${{ formatCurrency(data.costo_unitario_total_ars) }}
            </div>
          </template>
        </Column>

        <Column field="arancel_referencia_ars" header="Arancel de Referencia" style="width: 180px">
          <template #body="{ data }">
            <div class="font-semibold text-slate-100 font-mono text-sm">
              ${{ formatCurrency(data.arancel_referencia_ars) }}
            </div>
            <div class="text-[10px] text-emerald-400 font-mono">
              Margen: {{ data.margen_estimado_porcentaje }}%
            </div>
          </template>
        </Column>

        <Column header="Acciones" style="width: 120px">
          <template #body="{ data }">
            <div class="flex items-center gap-1.5">
              <button @click="verDetalle(data)" title="Ver Desglose Exacto" class="p-1.5 text-slate-400 hover:text-sky-400 hover:bg-slate-800 rounded">
                <i class="pi pi-eye"></i>
              </button>
              <button @click="editDeterminacion(data)" title="Editar" class="p-1.5 text-slate-400 hover:text-emerald-400 hover:bg-slate-800 rounded">
                <i class="pi pi-pencil"></i>
              </button>
              <button @click="confirmDelete(data)" title="Eliminar" class="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded">
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Modal Desglose de Costos (Drill-down) -->
    <Dialog v-model:visible="detalleDialog" modal header="Desglose Analítico y Exacto de Costo" :style="{ width: '680px' }">
      <div v-if="selectedDetalle" class="space-y-4 text-xs">
        <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 flex justify-between items-center">
          <div>
            <div class="text-sm font-bold text-slate-100">{{ selectedDetalle.nombre }}</div>
            <div class="text-slate-400 mt-0.5">Código: {{ selectedDetalle.codigo || 'N/A' }} | Sección: {{ selectedDetalle.seccion }}</div>
          </div>
          <div class="text-right">
            <span class="text-[10px] uppercase font-bold text-slate-400 block">Equipo Asignado</span>
            <span class="font-semibold text-emerald-400">{{ selectedDetalle.equipo?.nombre || 'Manual' }}</span>
          </div>
        </div>

        <!-- Lista de Insumos y Consumibles Utilizados -->
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <h4 class="font-bold text-slate-300 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
              <i class="pi pi-list text-emerald-400"></i>
              <span>Reactivos, Calibradores, Controles y Lavados ({{ selectedDetalle.insumos_asociados?.length || 0 }})</span>
            </h4>
            <span class="text-[11px] font-mono text-emerald-400 font-bold">
              Total Insumos: USD ${{ formatHighPrecision(selectedDetalle.costo_reactivos_usd) }} (ARS ${{ formatCurrency(selectedDetalle.costo_reactivos_ars) }})
            </span>
          </div>

          <div class="space-y-1.5 max-h-56 overflow-y-auto pr-1">
            <div v-for="item in selectedDetalle.insumos_asociados" :key="item.id"
              class="p-2.5 bg-slate-950 rounded-xl border border-slate-800/80 flex items-center justify-between">
              <div class="space-y-0.5">
                <div class="flex items-center gap-2">
                  <span class="font-mono text-xs font-bold text-slate-200">{{ item.insumo?.codigo || '-' }}</span>
                  <span class="font-semibold text-white">{{ item.insumo?.nombre }}</span>
                  <span class="text-[9px] px-1.5 py-0.2 rounded border font-bold uppercase"
                    :class="getTipoBadgeClass(item.insumo?.tipo || 'otro')">
                    {{ formatTipo(item.insumo?.tipo || 'otro') }}
                  </span>
                  <span
                    v-if="Number(item.cantidad_requerida) !== 1"
                    class="text-[9px] px-1.5 py-0.2 rounded border font-bold font-mono bg-amber-950 text-amber-300 border-amber-800"
                    title="Cantidad utilizada por determinación"
                  >
                    ×{{ formatNumber(item.cantidad_requerida) }}
                  </span>
                </div>
                <div class="text-[10px] text-slate-400 font-mono">
                  Fórmula: ({{ item.insumo?.moneda }} ${{ formatCurrency(item.insumo?.costo_presentacion) }} × {{ formatNumber(item.insumo?.unidades_compradas_periodo || 1) }}) ÷ {{ formatNumber(item.insumo?.determinaciones_periodo || 1) }} tests
                </div>
              </div>
              <div class="text-right">
                <div class="font-mono font-bold text-emerald-400 text-xs">
                  USD ${{ formatHighPrecision(item.costo_subtotal_usd) }}
                </div>
                <div class="text-[10px] font-mono text-slate-400">
                  ARS ${{ formatCurrency(item.costo_subtotal_ars) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Estructura del Costo Total -->
        <div class="space-y-2 pt-2 border-t border-slate-800">
          <h4 class="font-bold text-slate-300 uppercase tracking-wider text-[10px]">Resumen de Costo Unitario</h4>

          <div class="grid grid-cols-2 gap-2">
            <div class="p-2.5 bg-slate-900 rounded-lg border border-slate-800 flex justify-between items-center">
              <span class="text-slate-400">1. Insumos y Reactivos:</span>
              <span class="font-semibold text-slate-200 font-mono">USD ${{ formatHighPrecision(selectedDetalle.costo_reactivos_usd) }}</span>
            </div>
            <div class="p-2.5 bg-slate-900 rounded-lg border border-slate-800 flex justify-between items-center">
              <span class="text-slate-400">2. Autoanalizador / Test:</span>
              <span class="font-semibold text-slate-200 font-mono">USD ${{ formatHighPrecision(selectedDetalle.costo_equipo_usd) }}</span>
            </div>
          </div>

          <div class="flex justify-between items-center p-3 bg-rose-950/40 rounded-xl border border-rose-900/60 font-bold text-sm text-rose-300">
            <span>Costo Unitario Total por Determinación</span>
            <div class="text-right">
              <div>USD ${{ formatHighPrecision(selectedDetalle.costo_unitario_total_usd) }}</div>
              <div class="text-xs font-normal text-rose-400/80">ARS ${{ formatCurrency(selectedDetalle.costo_unitario_total_ars) }}</div>
            </div>
          </div>
        </div>

        <!-- Rentabilidad -->
        <div class="p-3 bg-emerald-950/30 rounded-xl border border-emerald-900/60 flex justify-between items-center">
          <div>
            <div class="text-[11px] text-emerald-400 font-semibold">Arancel Referencia: ${{ formatCurrency(selectedDetalle.arancel_referencia_ars) }} (USD ${{ formatCurrency(selectedDetalle.arancel_referencia_usd) }})</div>
            <div class="text-xs text-slate-300 font-bold">Margen Bruto por Test: ${{ formatCurrency(selectedDetalle.margen_bruto_ars) }}</div>
          </div>
          <div class="text-right">
            <div class="text-lg font-black text-emerald-400">{{ selectedDetalle.margen_estimado_porcentaje }}%</div>
            <div class="text-[10px] text-slate-400">Rentabilidad Bruta</div>
          </div>
        </div>
      </div>
    </Dialog>

    <!-- Modal Formulario Creación / Edición -->
    <Dialog v-model:visible="formDialog" modal :header="formDet.id ? 'Editar Determinación' : 'Nueva Determinación'" :style="{ width: '680px' }">
      <form @submit.prevent="saveDeterminacion" class="space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Nombre de la Práctica *</label>
            <input v-model="formDet.nombre" required class="form-input text-xs" placeholder="Ej: Colesterol Total" />
          </div>
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Código Interno</label>
            <input v-model="formDet.codigo" class="form-input text-xs" placeholder="Ej: DET-004" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Sección *</label>
            <select v-model="formDet.seccion" required class="form-input text-xs">
              <option v-for="sec in seccionesList" :key="sec.id" :value="sec.nombre">{{ sec.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Equipo Asociado</label>
            <select v-model="formDet.equipo_id" class="form-input text-xs">
              <option :value="null">Ninguno / Manual (Sin prorrateo de equipo)</option>
              <option v-for="eq in equipos" :key="eq.id" :value="eq.id">{{ eq.nombre }} ({{ eq.seccion }})</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Arancel de Venta Ref. (ARS) *</label>
            <input v-model.number="formDet.arancel_referencia_ars" type="number" step="any" required class="form-input text-xs" placeholder="Ej: 5200" />
          </div>
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Tiempo de Proceso Técnico (min)</label>
            <input v-model.number="formDet.tiempo_proceso_minutos" type="number" step="any" class="form-input text-xs" />
          </div>
        </div>

        <!-- Insumos Receta con MultiSelect Buscable -->
        <div class="pt-2 border-t border-slate-800 space-y-3">
          <div class="flex justify-between items-center">
            <div>
              <span class="font-bold text-slate-200 block">Componentes Utilizados (Reactivos, Calibradores, Controles, Lavados)</span>
              <span class="text-[10px] text-slate-400">Buscá y seleccioná los insumos que intervienen y ajustá la cantidad que consume cada determinación (por defecto 1)</span>
            </div>
            <div v-if="selectedInsumoIds.length > 0" class="text-right">
              <span class="text-[10px] text-slate-400 block">Total Reactivos:</span>
              <span class="font-mono text-xs font-bold text-emerald-400">
                USD ${{ formatHighPrecision(formCostoTotalInsumosUsd) }} <span class="text-[10px] text-slate-400">(${{ formatCurrency(formCostoTotalInsumosArs) }} ARS)</span>
              </span>
            </div>
          </div>

          <!-- MultiSelect con Filtro / Búsqueda -->
          <div class="space-y-2">
            <MultiSelect
              v-model="selectedInsumoIds"
              :options="insumosList"
              optionLabel="nombre"
              optionValue="id"
              filter
              filterPlaceholder="Buscar por nombre, código o marca..."
              placeholder="Buscar y seleccionar reactivos, calibradores, controles y lavados..."
              class="w-full text-xs"
              display="chip"
              :maxSelectedLabels="4"
            >
              <template #option="{ option }">
                <div class="flex items-center justify-between w-full py-1 text-xs">
                  <div class="flex items-center gap-2">
                    <span class="font-mono font-bold text-emerald-400">{{ option.codigo || '-' }}</span>
                    <span class="text-slate-100 font-medium">{{ option.nombre }}</span>
                    <span class="text-[9px] px-1.5 py-0.5 rounded border font-bold uppercase" :class="getTipoBadgeClass(option.tipo)">
                      {{ formatTipo(option.tipo) }}
                    </span>
                  </div>
                  <div class="font-mono text-emerald-400 font-semibold ml-4">
                    USD ${{ formatHighPrecision(option.costo_por_determinacion_usd) }}
                  </div>
                </div>
              </template>
            </MultiSelect>
          </div>

          <!-- Lista Visual de Insumos Seleccionados -->
          <div v-if="selectedInsumosDetails.length > 0" class="space-y-1.5 max-h-48 overflow-y-auto pr-1">
            <div
              v-for="ins in selectedInsumosDetails"
              :key="ins.id"
              class="p-2.5 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between text-xs"
            >
              <div class="flex items-center gap-2">
                <span class="font-mono text-xs font-bold text-emerald-400">{{ ins.codigo || '-' }}</span>
                <span class="font-semibold text-slate-200">{{ ins.nombre }}</span>
                <span class="text-[9px] px-1.5 py-0.5 rounded border font-bold uppercase" :class="getTipoBadgeClass(ins.tipo)">
                  {{ formatTipo(ins.tipo) }}
                </span>
              </div>
              <div class="flex items-center gap-3">
                <!-- Cantidad utilizada por determinación -->
                <div class="flex items-center gap-1.5" title="Cantidad de unidades de este componente que consume una determinación (ej: 2 tubos)">
                  <span class="text-[10px] text-slate-400 uppercase tracking-wider">Cant.</span>
                  <input
                    type="number"
                    step="any"
                    min="0.0001"
                    :value="getCantidad(ins.id)"
                    @input="setCantidad(ins.id, ($event.target as HTMLInputElement).value)"
                    class="form-input !w-20 !py-1 !px-2 text-center font-mono font-bold text-xs text-white"
                    :class="getCantidad(ins.id) !== 1 ? '!border-amber-500/60 !text-amber-300' : ''"
                  />
                </div>
                <div class="text-right min-w-[110px]">
                  <span class="font-mono text-emerald-400 font-bold block">
                    USD ${{ formatHighPrecision(Number(ins.costo_por_determinacion_usd || 0) * getCantidad(ins.id)) }}
                  </span>
                  <span v-if="getCantidad(ins.id) !== 1" class="text-[10px] font-mono text-slate-500 block">
                    {{ formatNumber(getCantidad(ins.id)) }} × ${{ formatHighPrecision(ins.costo_por_determinacion_usd) }}
                  </span>
                </div>
                <button
                  type="button"
                  @click="removeInsumoId(ins.id)"
                  title="Quitar componente"
                  class="p-1 text-slate-500 hover:text-rose-400 rounded hover:bg-slate-900"
                >
                  <i class="pi pi-times text-xs"></i>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="p-4 text-center text-slate-500 bg-slate-950 rounded-xl border border-dashed border-slate-800">
            No has seleccionado insumos para esta determinación. Abrí el buscador arriba para agregar reactivos y consumibles.
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-4 border-t border-slate-800">
          <button type="button" @click="formDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Guardar Determinación</button>
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import { apiClient } from '@/services/api';
import type { Determinacion, Equipo, Insumo, SeccionLaboratorio } from '@/types';

const toast = useToast();
const confirm = useConfirm();

const loading = ref(false);
const recalculando = ref(false);
const determinaciones = ref<Determinacion[]>([]);
const equipos = ref<Equipo[]>([]);
const insumosList = ref<Insumo[]>([]);
const seccionesList = ref<SeccionLaboratorio[]>([]);

const searchQuery = ref('');
const selectedSeccion = ref('');

const detalleDialog = ref(false);
const selectedDetalle = ref<Determinacion | null>(null);

const formDialog = ref(false);
const formDet = ref<any>({
  id: null,
  nombre: '',
  codigo: '',
  seccion: 'Química Clínica',
  equipo_id: null,
  tiempo_proceso_minutos: 0,
  arancel_referencia_ars: 5200,
});

const selectedInsumoIds = ref<number[]>([]);
// Cantidad requerida por insumo (insumo_id -> cantidad). Default 1.
const insumoCantidades = ref<Record<number, number>>({});

const getCantidad = (id: number): number => {
  const c = Number(insumoCantidades.value[id]);
  return c > 0 ? c : 1;
};

const setCantidad = (id: number, val: number | string) => {
  const n = Number(val);
  insumoCantidades.value[id] = n > 0 ? n : 1;
};

// Al agregar insumos desde el MultiSelect, inicializar cantidad 1 si no tienen
watch(selectedInsumoIds, (ids) => {
  ids.forEach((id) => {
    if (!insumoCantidades.value[id]) insumoCantidades.value[id] = 1;
  });
});

const selectedInsumosDetails = computed(() => {
  return insumosList.value.filter(ins => selectedInsumoIds.value.includes(ins.id));
});

const formCostoTotalInsumosUsd = computed(() => {
  return selectedInsumosDetails.value.reduce(
    (acc, curr) => acc + Number(curr.costo_por_determinacion_usd || 0) * getCantidad(curr.id), 0
  );
});

const formCostoTotalInsumosArs = computed(() => {
  return selectedInsumosDetails.value.reduce(
    (acc, curr) => acc + Number(curr.costo_unitario_ars || 0) * getCantidad(curr.id), 0
  );
});

const removeInsumoId = (id: number) => {
  selectedInsumoIds.value = selectedInsumoIds.value.filter(insId => insId !== id);
  delete insumoCantidades.value[id];
};

const formatCurrency = (val: number | string | undefined | null) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const formatNumber = (val: number | string | undefined | null) => {
  return Number(val || 0).toLocaleString('es-AR', { maximumFractionDigits: 2 });
};

const formatHighPrecision = (val: number | string | undefined | null) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 4, maximumFractionDigits: 6 });
};

const formatTipo = (t: string) => {
  const map: any = {
    reactivo: 'Reactivo Específico',
    calibrador: 'Calibrador',
    control: 'Control Calidad',
    solucion_lavado: 'Solución Lavado',
    descartable_extraccion: 'Extracción',
    descartable_equipo: 'Equipo',
    otro: 'Otro'
  };
  return map[t] || t;
};

const getTipoBadgeClass = (t: string) => {
  const map: any = {
    reactivo: 'bg-emerald-950 text-emerald-400 border-emerald-800',
    calibrador: 'bg-purple-950 text-purple-400 border-purple-800',
    control: 'bg-amber-950 text-amber-400 border-amber-800',
    solucion_lavado: 'bg-cyan-950 text-cyan-400 border-cyan-800',
    descartable_extraccion: 'bg-blue-950 text-blue-400 border-blue-800',
    descartable_equipo: 'bg-slate-800 text-slate-300 border-slate-700',
    otro: 'bg-slate-800 text-slate-400 border-slate-700'
  };
  return map[t] || 'bg-slate-800 text-slate-300 border-slate-700';
};

const filteredDeterminaciones = computed(() => {
  return determinaciones.value.filter((d) => {
    const matchesSearch = !searchQuery.value ||
      d.nombre.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (d.codigo && d.codigo.toLowerCase().includes(searchQuery.value.toLowerCase()));
    const matchesSeccion = !selectedSeccion.value || d.seccion === selectedSeccion.value;
    return matchesSearch && matchesSeccion;
  });
});

const loadData = async () => {
  loading.value = true;
  try {
    const results = await Promise.allSettled([
      apiClient.get('/determinaciones'),
      apiClient.get('/equipos'),
      apiClient.get('/insumos'),
      apiClient.get('/secciones')
    ]);
    if (results[0].status === 'fulfilled') determinaciones.value = results[0].value.data;
    if (results[1].status === 'fulfilled') equipos.value = results[1].value.data;
    if (results[2].status === 'fulfilled') insumosList.value = results[2].value.data;
    if (results[3].status === 'fulfilled') seccionesList.value = results[3].value.data;
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar algunos datos de determinaciones', life: 3000 });
  } finally {
    loading.value = false;
  }
};

const recalcularTodos = async () => {
  recalculando.value = true;
  try {
    const res = await apiClient.post('/determinaciones/recalcular-todos');
    toast.add({ severity: 'success', summary: 'Completado', detail: res.data.message, life: 3000 });
    await loadData();
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al recalcular costos', life: 3000 });
  } finally {
    recalculando.value = false;
  }
};

const verDetalle = (det: Determinacion) => {
  selectedDetalle.value = det;
  detalleDialog.value = true;
};

const openNewDialog = () => {
  formDet.value = {
    id: null,
    nombre: '',
    codigo: '',
    seccion: 'Química Clínica',
    equipo_id: equipos.value[0]?.id || null,
    tiempo_proceso_minutos: 0,
    arancel_referencia_ars: 5200,
  };
  selectedInsumoIds.value = [];
  insumoCantidades.value = {};
  formDialog.value = true;
};

const editDeterminacion = (det: Determinacion) => {
  formDet.value = {
    id: det.id,
    nombre: det.nombre,
    codigo: det.codigo,
    seccion: det.seccion,
    equipo_id: det.equipo_id,
    tiempo_proceso_minutos: det.tiempo_proceso_minutos,
    arancel_referencia_ars: det.arancel_referencia_ars,
  };
  const asociados = det.insumos_asociados || [];
  insumoCantidades.value = Object.fromEntries(
    asociados.map((i) => [i.insumo_id, Number(i.cantidad_requerida) > 0 ? Number(i.cantidad_requerida) : 1])
  );
  selectedInsumoIds.value = asociados.map((i) => i.insumo_id);
  formDialog.value = true;
};

const saveDeterminacion = async () => {
  try {
    const payload = {
      ...formDet.value,
      insumos: selectedInsumoIds.value.map(id => ({
        insumo_id: id,
        cantidad_requerida: getCantidad(id)
      }))
    };
    if (formDet.value.id) {
      await apiClient.put(`/determinaciones/${formDet.value.id}`, payload);
      toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Determinación actualizada correctamente', life: 3000 });
    } else {
      await apiClient.post('/determinaciones', payload);
      toast.add({ severity: 'success', summary: 'Creado', detail: 'Determinación creada y costeada', life: 3000 });
    }
    formDialog.value = false;
    await loadData();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'Error al guardar', life: 3000 });
  }
};

const confirmDelete = (det: Determinacion) => {
  confirm.require({
    message: `¿Está seguro de eliminar la determinación "${det.nombre}"?`,
    header: 'Confirmar Eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await apiClient.delete(`/determinaciones/${det.id}`);
        toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Determinación eliminada', life: 3000 });
        await loadData();
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar', life: 3000 });
      }
    }
  });
};

onMounted(() => {
  loadData();
});
</script>
