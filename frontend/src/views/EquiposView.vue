<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight text-slate-900">Equipos y Autoanalizadores</h1>
        <p class="text-sm text-slate-500">Prorrateo de costos fijos mensuales (alquiler, mantenimiento oficial, amortización) por volumen de determinaciones</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="openNewDialog" class="btn-primary text-xs">
          <i class="pi pi-plus"></i>
          <span>Nuevo Analizador</span>
        </button>
      </div>
    </div>

    <!-- Info Banner Explicativo -->
    <div class="p-4 bg-white border border-slate-200 rounded-2xl flex items-start gap-3 shadow-lg">
      <i class="pi pi-info-circle text-sky-600 text-lg mt-0.5"></i>
      <div class="text-xs text-slate-600 space-y-1">
        <span class="font-bold text-slate-900 block">¿Cómo se computa el costo del equipo?</span>
        <p class="text-slate-500 leading-relaxed">
          En esta pantalla se cargan exclusivamente los <strong class="text-slate-800">costos fijos del autoanalizador</strong> (Alquiler/Comodato mensual, Abono de Service Técnico Oficial, Amortización contable y Abono de Calibración/QC). La suma mensual se divide por el volumen de tests mensual que procesa el equipo.
        </p>
        <p class="text-slate-500">
          💡 <span class="text-brand-600 font-semibold">Consumibles y Reactivos:</span> Las soluciones de lavado (Wash Solutions), cubetas de reacción, reactivos y calibradores se costean con exactitud lote a lote en la tabla de <router-link to="/insumos" class="text-brand-600 underline font-semibold">Insumos</router-link>.
        </p>
      </div>
    </div>

    <!-- Table Container -->
    <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xl space-y-4">
      <DataTable
        :value="equipos"
        :paginator="true"
        :rows="10"
        :loading="loading"
        responsiveLayout="scroll"
        class="text-xs"
      >
        <Column field="nombre" header="Analizador / Equipo" :sortable="true">
          <template #body="{ data }">
            <div class="font-semibold text-slate-900 text-sm">{{ data.nombre }}</div>
            <div class="text-[11px] text-slate-500">{{ data.marca || 'Sin marca' }} {{ data.modelo || '' }} • <span class="text-brand-600 font-medium">{{ data.seccion }}</span></div>
          </template>
        </Column>

        <Column field="volumen_mensual_estimado" header="Volumen Mensual" :sortable="true" style="width: 160px">
          <template #body="{ data }">
            <span class="font-mono text-slate-800 font-semibold">{{ formatNumber(data.volumen_mensual_estimado) }} tests/mes</span>
          </template>
        </Column>

        <Column header="Costos Fijos Mensuales">
          <template #body="{ data }">
            <div class="space-y-0.5 text-[11px] font-mono text-slate-600">
              <div v-if="data.costo_alquiler_mensual > 0">
                <span class="text-slate-500">Alquiler:</span> {{ data.moneda || 'USD' }} ${{ formatCurrency(data.costo_alquiler_mensual) }}
              </div>
              <div v-if="data.costo_mantenimiento_mensual > 0">
                <span class="text-slate-500">Mantenimiento:</span> {{ data.moneda || 'USD' }} ${{ formatCurrency(data.costo_mantenimiento_mensual) }}
              </div>
              <div v-if="data.costo_amortizacion_mensual > 0">
                <span class="text-slate-500">Amortización:</span> {{ data.moneda || 'USD' }} ${{ formatCurrency(data.costo_amortizacion_mensual) }}
              </div>
              <div v-if="data.costo_calibracion_controles_mensual > 0">
                <span class="text-slate-500">Serv. Calibración:</span> {{ data.moneda || 'USD' }} ${{ formatCurrency(data.costo_calibracion_controles_mensual) }}
              </div>
            </div>
          </template>
        </Column>

        <Column field="costo_total_mensual" header="Gasto Mensual Total" :sortable="true" style="width: 180px">
          <template #body="{ data }">
            <div class="font-bold text-sky-600 font-mono text-sm">
              USD ${{ formatCurrency(data.costo_total_mensual_usd) }}
            </div>
            <div class="text-[10px] text-slate-500 font-mono">
              ARS ${{ formatCurrency(data.costo_total_mensual) }}
            </div>
          </template>
        </Column>

        <Column field="costo_unitario_por_test" header="Costo / Test" :sortable="true" style="width: 180px">
          <template #body="{ data }">
            <div class="font-bold text-brand-600 font-mono text-sm">
              USD ${{ formatHighPrecision(data.costo_unitario_por_test_usd) }}
            </div>
            <div class="text-[10px] text-slate-500 font-mono">
              ARS ${{ formatCurrency(data.costo_unitario_por_test) }}/test
            </div>
          </template>
        </Column>

        <Column header="Acciones" style="width: 100px">
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <button @click="editEquipo(data)" title="Editar" class="p-1.5 text-slate-500 hover:text-brand-600 hover:bg-slate-100 rounded">
                <i class="pi pi-pencil"></i>
              </button>
              <button @click="confirmDelete(data)" title="Eliminar" class="p-1.5 text-slate-500 hover:text-rose-600 hover:bg-slate-100 rounded">
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Form Dialog -->
    <Dialog v-model:visible="formDialog" modal :header="formEq.id ? 'Editar Analizador' : 'Nuevo Analizador'" :style="{ width: '620px' }">
      <form @submit.prevent="saveEquipo" class="space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Nombre Analizador / Equipo *</label>
            <input v-model="formEq.nombre" required class="form-input text-xs" placeholder="Ej: Beckman Coulter AU480" />
          </div>
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Sección de Laboratorio *</label>
            <select v-model="formEq.seccion" required class="form-input text-xs">
              <option v-for="sec in seccionesList" :key="sec.id" :value="sec.nombre">{{ sec.nombre }}</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Marca / Fabricante</label>
            <input v-model="formEq.marca" class="form-input text-xs" placeholder="Ej: Beckman Coulter, Roche" />
          </div>
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Modelo</label>
            <input v-model="formEq.modelo" class="form-input text-xs" placeholder="Ej: AU480, c311" />
          </div>
        </div>

        <!-- Moneda y Tipo de Cambio -->
        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
          <div class="text-[11px] font-bold uppercase tracking-wider text-brand-600 flex items-center gap-1.5">
            <i class="pi pi-dollar"></i>
            <span>Moneda de los Contratos y Tipo de Cambio</span>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-semibold text-slate-600 mb-1">Moneda de los Costos *</label>
              <select v-model="formEq.moneda" class="form-input text-xs font-semibold">
                <option value="USD">USD (Dólares)</option>
                <option value="ARS">ARS (Pesos)</option>
              </select>
            </div>
            <div>
              <label class="block font-semibold text-amber-600 mb-1">Tipo de Cambio USD/ARS *</label>
              <input v-model.number="formEq.tipo_cambio_al_costear" type="number" step="any" required class="form-input text-xs" />
            </div>
          </div>
        </div>

        <!-- Costos Fijos Mensuales del Equipo -->
        <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
          <div class="text-[11px] font-bold uppercase tracking-wider text-sky-600 flex items-center gap-1.5">
            <i class="pi pi-server"></i>
            <span>Costos Fijos Propios del Analizador (en {{ formEq.moneda }})</span>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-semibold text-slate-600 mb-1">Alquiler / Comodato Mensual</label>
              <input v-model.number="formEq.costo_alquiler_mensual" type="number" step="any" class="form-input text-xs" placeholder="0.00" />
            </div>
            <div>
              <label class="block font-semibold text-slate-600 mb-1">Service Técnico / Mantenimiento Mensual</label>
              <input v-model.number="formEq.costo_mantenimiento_mensual" type="number" step="any" class="form-input text-xs" placeholder="0.00" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-semibold text-slate-600 mb-1">Amortización Mensual (si es propio)</label>
              <input v-model.number="formEq.costo_amortizacion_mensual" type="number" step="any" class="form-input text-xs" placeholder="0.00" />
            </div>
            <div>
              <label class="block font-semibold text-slate-600 mb-1">Abono Servicio Calibración Técnica Oficial</label>
              <input v-model.number="formEq.costo_calibracion_controles_mensual" type="number" step="any" class="form-input text-xs" placeholder="0.00" />
            </div>
          </div>

          <div>
            <label class="block font-semibold text-brand-600 mb-1">Volumen Mensual de Determinaciones Procesadas *</label>
            <input v-model.number="formEq.volumen_mensual_estimado" type="number" min="1" required class="form-input text-xs" placeholder="Ej: 30000 tests/mes" />
            <p class="text-[10px] text-slate-500 mt-0.5">Cantidad total de determinaciones que procesa este analizador por mes para prorratear el costo</p>
          </div>

          <!-- Live Preview Box -->
          <div class="p-2.5 bg-white rounded-lg border border-slate-200 flex items-center justify-between text-xs">
            <div>
              <span class="text-slate-500 block text-[11px]">Gasto Fijo Total Mensual:</span>
              <span class="text-sky-600 font-bold font-mono text-xs">
                USD ${{ previewTotalMensualUsd }} <span class="text-slate-500 font-normal">(${{ previewTotalMensualArs }} ARS)</span>
              </span>
            </div>
            <div class="text-right">
              <span class="text-slate-500 block text-[10px]">Costo Fijo Prorrateado / Test:</span>
              <span class="text-brand-600 font-black font-mono text-sm">
                USD ${{ previewCostoTestUsd }} <span class="text-xs text-slate-500">(${{ previewCostoTestArs }} ARS)</span>
              </span>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-4 border-t border-slate-200">
          <button type="button" @click="formDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Guardar Analizador</button>
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
import type { Equipo, SeccionLaboratorio } from '@/types';

const toast = useToast();
const confirm = useConfirm();

const loading = ref(false);
const equipos = ref<Equipo[]>([]);
const seccionesList = ref<SeccionLaboratorio[]>([]);
const formDialog = ref(false);

const formEq = ref<any>({
  id: null,
  nombre: '',
  marca: '',
  modelo: '',
  seccion: 'Química Clínica',
  moneda: 'USD',
  tipo_cambio_al_costear: 1200,
  costo_alquiler_mensual: 0,
  costo_mantenimiento_mensual: 0,
  costo_amortizacion_mensual: 0,
  costo_calibracion_controles_mensual: 0,
  volumen_mensual_estimado: 30000,
  consumibles_mantenimiento: []
});

const previewTotalMensualBase = computed(() => {
  return Number(formEq.value.costo_alquiler_mensual || 0) +
    Number(formEq.value.costo_mantenimiento_mensual || 0) +
    Number(formEq.value.costo_amortizacion_mensual || 0) +
    Number(formEq.value.costo_calibracion_controles_mensual || 0);
});

const previewTotalMensualUsd = computed(() => {
  const base = previewTotalMensualBase.value;
  const tc = Number(formEq.value.tipo_cambio_al_costear || 1200);
  if (formEq.value.moneda === 'ARS') {
    return (base / (tc || 1)).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  return base.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
});

const previewTotalMensualArs = computed(() => {
  const base = previewTotalMensualBase.value;
  const tc = Number(formEq.value.tipo_cambio_al_costear || 1200);
  if (formEq.value.moneda === 'USD') {
    return (base * tc).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  return base.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
});

const previewCostoTestUsd = computed(() => {
  const vol = Math.max(Number(formEq.value.volumen_mensual_estimado || 1), 1);
  const base = previewTotalMensualBase.value;
  const tc = Number(formEq.value.tipo_cambio_al_costear || 1200);
  let totalUsd = base;
  if (formEq.value.moneda === 'ARS') {
    totalUsd = base / (tc || 1);
  }
  return (totalUsd / vol).toFixed(6);
});

const previewCostoTestArs = computed(() => {
  const vol = Math.max(Number(formEq.value.volumen_mensual_estimado || 1), 1);
  const base = previewTotalMensualBase.value;
  const tc = Number(formEq.value.tipo_cambio_al_costear || 1200);
  let totalArs = base;
  if (formEq.value.moneda === 'USD') {
    totalArs = base * tc;
  }
  return (totalArs / vol).toFixed(4);
});

const formatCurrency = (val: number | string | undefined | null) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const formatHighPrecision = (val: number | string | undefined | null) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 4, maximumFractionDigits: 6 });
};

const formatNumber = (val: number | string | undefined | null) => {
  return Number(val || 0).toLocaleString('es-AR');
};

const loadEquipos = async () => {
  loading.value = true;
  try {
    const results = await Promise.allSettled([
      apiClient.get('/equipos'),
      apiClient.get('/secciones')
    ]);
    if (results[0].status === 'fulfilled') equipos.value = results[0].value.data;
    if (results[1].status === 'fulfilled') seccionesList.value = results[1].value.data;
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los equipos', life: 3000 });
  } finally {
    loading.value = false;
  }
};

const openNewDialog = () => {
  formEq.value = {
    id: null,
    nombre: '',
    marca: '',
    modelo: '',
    seccion: 'Química Clínica',
    moneda: 'USD',
    tipo_cambio_al_costear: 1200,
    costo_alquiler_mensual: 200,
    costo_mantenimiento_mensual: 100,
    costo_amortizacion_mensual: 0,
    costo_calibracion_controles_mensual: 50,
    volumen_mensual_estimado: 30000,
    consumibles_mantenimiento: []
  };
  formDialog.value = true;
};

const editEquipo = (eq: Equipo) => {
  formEq.value = {
    id: eq.id,
    nombre: eq.nombre,
    marca: eq.marca,
    modelo: eq.modelo,
    seccion: eq.seccion,
    moneda: eq.moneda || 'USD',
    tipo_cambio_al_costear: Number(eq.tipo_cambio_al_costear || 1200),
    costo_alquiler_mensual: Number(eq.costo_alquiler_mensual || 0),
    costo_mantenimiento_mensual: Number(eq.costo_mantenimiento_mensual || 0),
    costo_amortizacion_mensual: Number(eq.costo_amortizacion_mensual || 0),
    costo_calibracion_controles_mensual: Number(eq.costo_calibracion_controles_mensual || 0),
    volumen_mensual_estimado: Number(eq.volumen_mensual_estimado || 1000),
    consumibles_mantenimiento: [...(eq.consumibles_mantenimiento || [])]
  };
  formDialog.value = true;
};

const saveEquipo = async () => {
  try {
    if (formEq.value.id) {
      await apiClient.put(`/equipos/${formEq.value.id}`, formEq.value);
      toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Equipo actualizado correctamente', life: 3000 });
    } else {
      await apiClient.post('/equipos', formEq.value);
      toast.add({ severity: 'success', summary: 'Creado', detail: 'Equipo registrado correctamente', life: 3000 });
    }
    formDialog.value = false;
    await loadEquipos();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'Error al guardar', life: 3000 });
  }
};

const confirmDelete = (eq: Equipo) => {
  confirm.require({
    message: `¿Está seguro de eliminar el equipo "${eq.nombre}"?`,
    header: 'Confirmar Eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await apiClient.delete(`/equipos/${eq.id}`);
        toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Equipo eliminado', life: 3000 });
        await loadEquipos();
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar el equipo', life: 3000 });
      }
    }
  });
};

onMounted(() => {
  loadEquipos();
});
</script>
