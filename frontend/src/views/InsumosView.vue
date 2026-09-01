<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight text-white">Insumos y Reactivos de Laboratorio</h1>
        <p class="text-sm text-slate-400">Maestro de reactivos específicos, calibradores compartidos, controles globales y soluciones de lavado</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="openNewDialog" class="btn-primary text-xs">
          <i class="pi pi-plus"></i>
          <span>Nuevo Insumo / Reactivo</span>
        </button>
      </div>
    </div>

    <!-- Table Container -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      <div class="flex flex-col sm:flex-row gap-4 justify-between items-center">
        <div class="relative w-full sm:w-80">
          <i class="pi pi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-sm"></i>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por código, nombre o marca..."
            class="form-input !pl-11 text-xs"
          />
        </div>
        <div class="flex items-center gap-2 w-full sm:w-auto">
          <select v-model="selectedBase" class="form-input text-xs w-full sm:w-44">
            <option value="">Todas las Bases</option>
            <option value="test">Por Tests / Determinación</option>
            <option value="paciente">Por Paciente / Extracción</option>
          </select>
          <select v-model="selectedTipo" class="form-input text-xs w-full sm:w-52">
            <option value="">Todos los Tipos</option>
            <option value="reactivo">Reactivo Específico</option>
            <option value="calibrador">Calibrador</option>
            <option value="control">Control de Calidad</option>
            <option value="solucion_lavado">Solución Lavado / Equipo</option>
            <option value="descartable_extraccion">Descartables Extracción</option>
            <option value="descartable_equipo">Descartables Equipo</option>
            <option value="otro">Otro</option>
          </select>
        </div>
      </div>

      <DataTable
        :value="filteredInsumos"
        :paginator="true"
        :rows="10"
        :loading="loading"
        responsiveLayout="scroll"
        class="text-xs"
      >
        <Column field="codigo" header="Código" :sortable="true" style="width: 110px">
          <template #body="{ data }">
            <span class="font-mono text-emerald-400 font-bold">{{ data.codigo || '-' }}</span>
          </template>
        </Column>

        <Column field="nombre" header="Insumo / Reactivo" :sortable="true">
          <template #body="{ data }">
            <div class="font-semibold text-slate-100">{{ data.nombre }}</div>
            <div class="text-[11px] text-slate-400">{{ data.marca_proveedor || 'Sin marca' }} • {{ data.presentacion || 'Unidad' }}</div>
          </template>
        </Column>

        <Column field="tipo" header="Tipo / Base" :sortable="true">
          <template #body="{ data }">
            <div class="space-y-1">
              <span
                class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border inline-block"
                :class="getTipoBadgeClass(data.tipo)">
                {{ formatTipo(data.tipo) }}
              </span>
              <div>
                <span
                  class="text-[9px] px-1.5 py-0.2 rounded font-semibold uppercase font-mono"
                  :class="data.base_calculo === 'paciente' ? 'bg-purple-950/80 text-purple-300 border border-purple-800' : 'bg-slate-800 text-slate-300 border border-slate-700'">
                  {{ data.base_calculo === 'paciente' ? 'Base: Paciente' : 'Base: Tests' }}
                </span>
              </div>
            </div>
          </template>
        </Column>

        <Column field="costo_presentacion" header="Costo Compra" :sortable="true">
          <template #body="{ data }">
            <span class="font-semibold text-slate-200">
              {{ data.moneda === 'USD' ? 'USD $' : '$' }}{{ formatCurrency(data.costo_presentacion) }}
            </span>
            <span v-if="data.moneda === 'USD'" class="block text-[10px] text-amber-400 font-mono">
              (TC: ${{ formatCurrency(data.tipo_cambio_al_costear) }})
            </span>
          </template>
        </Column>

        <Column header="Período (Consumo / Volumen)" :sortable="true" field="determinaciones_periodo">
          <template #body="{ data }">
            <div class="text-slate-300 font-mono text-[11px]">
              <span class="text-amber-400 font-semibold">{{ formatNumber(data.unidades_compradas_periodo || 1) }} compradas</span> /
              <span class="text-sky-400 font-semibold">
                {{ formatNumber(data.determinaciones_periodo || 1) }} {{ data.base_calculo === 'paciente' ? 'pacientes' : 'tests' }}
              </span>
            </div>
          </template>
        </Column>

        <Column field="costo_por_determinacion_usd" header="Costo Unitario" :sortable="true">
          <template #body="{ data }">
            <div class="font-bold font-mono text-emerald-400 text-sm">
              USD ${{ formatHighPrecision(data.costo_por_determinacion_usd) }}
            </div>
            <div class="text-[10px] text-slate-400 font-mono">
              ARS ${{ formatHighPrecision(data.costo_unitario_ars) }} <span class="text-slate-500">/ {{ data.base_calculo === 'paciente' ? 'paciente' : 'test' }}</span>
            </div>
          </template>
        </Column>

        <Column header="Acciones" style="width: 100px">
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <button @click="editInsumo(data)" title="Editar" class="p-1.5 text-slate-400 hover:text-emerald-400 hover:bg-slate-800 rounded">
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

    <!-- Dialog Form Insumo -->
    <Dialog v-model:visible="formDialog" modal :header="formIns.id ? 'Editar Insumo' : 'Nuevo Insumo / Consumible'" :style="{ width: '620px' }">
      <form @submit.prevent="saveInsumo" class="space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Nombre Insumo / Reactivo *</label>
            <input v-model="formIns.nombre" required class="form-input text-xs" placeholder="Ej: Reactivo Colesterol Total" />
          </div>
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Código del Fabricante / Interno</label>
            <input v-model="formIns.codigo" class="form-input text-xs" placeholder="Ej: OSR6216, BKDR0070-1" />
          </div>
        </div>

        <!-- Base de Cálculo y Tipo -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Tipo de Insumo *</label>
            <select v-model="formIns.tipo" required class="form-input text-xs">
              <option value="reactivo">Reactivo Específico</option>
              <option value="calibrador">Calibrador Multi-analito / Específico</option>
              <option value="control">Control de Calidad Global</option>
              <option value="solucion_lavado">Solución de Lavado / Consumible Equipo</option>
              <option value="descartable_extraccion">Descartable Extracción (Agujas, Tubos, Algodón)</option>
              <option value="descartable_equipo">Descartable de Equipo (Cubetas, Puntas)</option>
              <option value="otro">Otro</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold text-amber-400 mb-1">Base de Cálculo / Rendimiento *</label>
            <select v-model="formIns.base_calculo" required class="form-input text-xs font-semibold">
              <option value="test">Por Tests / Determinaciones (Reactivos, Calibradores, Lavados)</option>
              <option value="paciente">Por Paciente / Extracciones (Tubos, Agujas, Algodón, Descartables)</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Marca / Proveedor / Fabricante</label>
            <input v-model="formIns.marca_proveedor" class="form-input text-xs" placeholder="Ej: Beckman Coulter AU / BD Vacutainer" />
          </div>
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Presentación Comercial</label>
            <input v-model="formIns.presentacion" class="form-input text-xs" placeholder="Ej: Kit x 100 tests, Caja x 100 tubos" />
          </div>
        </div>

        <!-- Costos y Moneda de Compra -->
        <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
          <div class="text-[11px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
            <i class="pi pi-dollar"></i>
            <span>Costo de Compra del Insumo</span>
          </div>

          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block font-semibold text-slate-300 mb-1">Moneda *</label>
              <select v-model="formIns.moneda" class="form-input text-xs">
                <option value="USD">USD (Dólares)</option>
                <option value="ARS">ARS (Pesos)</option>
              </select>
            </div>
            <div>
              <label class="block font-semibold text-slate-300 mb-1">Costo Compra Unitario *</label>
              <input v-model.number="formIns.costo_presentacion" type="number" step="any" min="0.0001" required class="form-input text-xs" />
            </div>
            <div>
              <label class="block font-semibold text-amber-400 mb-1">Tipo de Cambio USD/ARS</label>
              <input v-model.number="formIns.tipo_cambio_al_costear" type="number" step="any" class="form-input text-xs" />
            </div>
          </div>
        </div>

        <!-- Parámetros del Período Real (Fórmula Exacta) -->
        <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
          <div class="text-[11px] font-bold uppercase tracking-wider text-sky-400 flex items-center gap-1.5">
            <i class="pi pi-chart-line"></i>
            <span>Parámetros del Período Real (Cálculo {{ formIns.base_calculo === 'paciente' ? 'por Paciente' : 'por Test' }})</span>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-semibold text-slate-300 mb-1">Unidades Compradas / Consumidas *</label>
              <input v-model.number="formIns.unidades_compradas_periodo" type="number" step="any" min="0.0001" required class="form-input text-xs" placeholder="Ej: 4" />
              <p class="text-[10px] text-slate-500 mt-0.5">Cantidad de reactivos/cajas consumidos en el período</p>
            </div>
            <div>
              <label class="block font-semibold text-slate-300 mb-1">
                {{ formIns.base_calculo === 'paciente' ? 'Pacientes Atendidos en el Período *' : 'Determinaciones Entregadas en el Período *' }}
              </label>
              <input v-model.number="formIns.determinaciones_periodo" type="number" step="any" min="1" required class="form-input text-xs" :placeholder="formIns.base_calculo === 'paciente' ? 'Ej: 1500 pacientes' : 'Ej: 31445 tests'" />
              <p class="text-[10px] text-slate-500 mt-0.5">
                {{ formIns.base_calculo === 'paciente' ? 'Total de pacientes/extracciones en el período' : 'Total de tests entregados que usan este insumo' }}
              </p>
            </div>
          </div>

          <!-- Live Preview Card -->
          <div class="p-2.5 bg-slate-900 rounded-lg border border-slate-700/60 flex items-center justify-between text-xs">
            <div>
              <span class="text-slate-400 block text-[11px]">Fórmula Resultante:</span>
              <span class="text-slate-300 font-mono text-[11px]">
                ({{ formIns.moneda }} ${{ formIns.costo_presentacion }} × {{ formIns.unidades_compradas_periodo }}) ÷ {{ Number(formIns.determinaciones_periodo || 1).toLocaleString('es-AR') }} {{ formIns.base_calculo === 'paciente' ? 'pacientes' : 'tests' }}
              </span>
            </div>
            <div class="text-right">
              <span class="text-slate-400 block text-[10px]">Costo Unitario / {{ formIns.base_calculo === 'paciente' ? 'Paciente' : 'Test' }}:</span>
              <span class="text-emerald-400 font-black font-mono text-sm">
                USD ${{ previewCostoUsd }} <span class="text-xs text-slate-400">(${{ previewCostoArs }} ARS)</span>
              </span>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-4 border-t border-slate-800">
          <button type="button" @click="formDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Guardar Insumo</button>
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import { apiClient } from '@/services/api';
import type { Insumo } from '@/types';

const toast = useToast();
const confirm = useConfirm();

const loading = ref(false);
const insumos = ref<Insumo[]>([]);
const searchQuery = ref('');
const selectedTipo = ref('');
const selectedBase = ref('');

const formDialog = ref(false);
const formIns = ref<any>({
  id: null,
  nombre: '',
  codigo: '',
  marca_proveedor: '',
  tipo: 'reactivo',
  base_calculo: 'test',
  presentacion: '',
  cantidad_por_presentacion: 1,
  unidad_medida: 'test',
  costo_presentacion: 69.2,
  moneda: 'USD',
  tipo_cambio_al_costear: 1200,
  unidades_compradas_periodo: 4,
  determinaciones_periodo: 31445,
  merma_estimada_porcentaje: 0,
});

const previewCostoUsd = computed(() => {
  const costo = Number(formIns.value.costo_presentacion || 0);
  const unidades = Number(formIns.value.unidades_compradas_periodo || 1);
  const tests = Number(formIns.value.determinaciones_periodo || 1);
  const tc = Number(formIns.value.tipo_cambio_al_costear || 1200);

  if (tests <= 0) return '0.000000';

  let unitUsd = (costo * unidades) / tests;
  if (formIns.value.moneda === 'ARS') {
    unitUsd = unitUsd / (tc || 1);
  }
  return unitUsd.toFixed(6);
});

const previewCostoArs = computed(() => {
  const unitUsd = Number(previewCostoUsd.value || 0);
  const tc = Number(formIns.value.tipo_cambio_al_costear || 1200);
  if (formIns.value.moneda === 'ARS') {
    const costo = Number(formIns.value.costo_presentacion || 0);
    const unidades = Number(formIns.value.unidades_compradas_periodo || 1);
    const tests = Number(formIns.value.determinaciones_periodo || 1);
    return ((costo * unidades) / tests).toFixed(4);
  }
  return (unitUsd * tc).toFixed(4);
});

const formatCurrency = (val: number) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const formatNumber = (val: number | string | undefined | null) => {
  return Number(val || 0).toLocaleString('es-AR', { maximumFractionDigits: 2 });
};

const formatHighPrecision = (val: number) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 4, maximumFractionDigits: 6 });
};

const formatTipo = (t: string) => {
  const map: any = {
    reactivo: 'Reactivo Específico',
    calibrador: 'Calibrador',
    control: 'Control Calidad',
    solucion_lavado: 'Solución Lavado',
    descartable_extraccion: 'Extracción',
    descartable_equipo: 'Descartable Equipo',
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

const filteredInsumos = computed(() => {
  return insumos.value.filter((i) => {
    const matchesSearch = !searchQuery.value ||
      i.nombre.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (i.codigo && i.codigo.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
      (i.marca_proveedor && i.marca_proveedor.toLowerCase().includes(searchQuery.value.toLowerCase()));
    const matchesTipo = !selectedTipo.value || i.tipo === selectedTipo.value;
    const matchesBase = !selectedBase.value || (i.base_calculo || 'test') === selectedBase.value;
    return matchesSearch && matchesTipo && matchesBase;
  });
});

const loadInsumos = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/insumos');
    insumos.value = response.data;
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los insumos', life: 3000 });
  } finally {
    loading.value = false;
  }
};

const openNewDialog = () => {
  formIns.value = {
    id: null,
    nombre: '',
    codigo: '',
    marca_proveedor: '',
    tipo: 'reactivo',
    base_calculo: 'test',
    presentacion: 'Kit de Ensayo',
    cantidad_por_presentacion: 1,
    unidad_medida: 'test',
    costo_presentacion: 69.2,
    moneda: 'USD',
    tipo_cambio_al_costear: 1200,
    unidades_compradas_periodo: 4,
    determinaciones_periodo: 31445,
    merma_estimada_porcentaje: 0,
  };
  formDialog.value = true;
};

const editInsumo = (ins: Insumo) => {
  formIns.value = {
    ...ins,
    costo_presentacion: Number(ins.costo_presentacion || 0),
    tipo_cambio_al_costear: Number(ins.tipo_cambio_al_costear || 1200),
    unidades_compradas_periodo: Number(ins.unidades_compradas_periodo || 1),
    determinaciones_periodo: Number(ins.determinaciones_periodo || 1),
    merma_estimada_porcentaje: Number(ins.merma_estimada_porcentaje || 0),
    base_calculo: ins.base_calculo || 'test'
  };
  formDialog.value = true;
};

const saveInsumo = async () => {
  try {
    if (formIns.value.id) {
      await apiClient.put(`/insumos/${formIns.value.id}`, formIns.value);
      toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Insumo actualizado correctamente', life: 3000 });
    } else {
      await apiClient.post('/insumos', formIns.value);
      toast.add({ severity: 'success', summary: 'Creado', detail: 'Insumo registrado', life: 3000 });
    }
    formDialog.value = false;
    await loadInsumos();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'Error al guardar', life: 3000 });
  }
};

const confirmDelete = (ins: Insumo) => {
  confirm.require({
    message: `¿Está seguro de eliminar el insumo "${ins.nombre}"?`,
    header: 'Confirmar Eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await apiClient.delete(`/insumos/${ins.id}`);
        toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Insumo eliminado', life: 3000 });
        await loadInsumos();
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar el insumo', life: 3000 });
      }
    }
  });
};

onMounted(() => {
  loadInsumos();
});
</script>
