<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-800">Conciliación de Compras y Producción</h1>
        <p class="text-sm text-slate-500">Control de desvíos: Consumo Teórico proyectado por determinaciones ejecutadas vs. Compras Reales</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs">
          <span class="text-slate-500">Período:</span>
          <select v-model.number="mes" class="bg-transparent text-slate-800 focus:outline-none">
            <option v-for="m in 12" :key="m" :value="m">{{ getNombreMes(m) }}</option>
          </select>
          <select v-model.number="anio" class="bg-transparent text-slate-800 focus:outline-none">
            <option :value="2024">2024</option>
            <option :value="2025">2025</option>
          </select>
        </div>
        <button @click="cargarConciliacion" :disabled="loading" class="btn-primary text-xs">
          <i class="pi pi-search" :class="{ 'pi-spin': loading }"></i>
          <span>Consultar Período</span>
        </button>
      </div>
    </div>

    <!-- Summary Banner -->
    <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-xs font-bold text-slate-600 uppercase tracking-wider">Auditoría de Insumos - {{ getNombreMes(mes) }} {{ anio }}</h3>
          <p class="text-xs text-slate-500 mt-0.5">Se marcan alertas rojas en desvíos superiores al ±15% entre compras e insumos proyectados por el LIS</p>
        </div>
      </div>

      <!-- DataTable -->
      <DataTable :value="conciliacionItems" :loading="loading" class="text-xs">
        <Column field="insumo_nombre" header="Insumo / Reactivo">
          <template #body="{ data }">
            <span class="font-semibold text-slate-800">{{ data.insumo_nombre }}</span>
          </template>
        </Column>

        <Column field="consumo_teorico_unidades" header="Consumo Teórico (LIS)">
          <template #body="{ data }">
            <div class="font-mono text-slate-600">{{ data.consumo_teorico_unidades }} un.</div>
            <div class="text-[10px] text-slate-500">${{ formatCurrency(data.consumo_teorico_ars) }}</div>
          </template>
        </Column>

        <Column field="compras_reales_unidades" header="Compras Registradas">
          <template #body="{ data }">
            <div class="font-mono text-slate-600">{{ data.compras_reales_unidades }} un.</div>
            <div class="text-[10px] text-slate-500">${{ formatCurrency(data.compras_reales_ars) }}</div>
          </template>
        </Column>

        <Column field="desvio_unidades" header="Desvío Físico">
          <template #body="{ data }">
            <span :class="data.desvio_unidades > 0 ? 'text-amber-600' : 'text-slate-500'">
              {{ data.desvio_unidades > 0 ? '+' : '' }}{{ data.desvio_unidades }} un.
            </span>
          </template>
        </Column>

        <Column field="desvio_porcentaje" header="Desvío %">
          <template #body="{ data }">
            <span
              class="px-2 py-0.5 rounded-full font-bold text-[11px]"
              :class="data.alerta ? 'bg-rose-50 text-rose-600 border border-rose-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'"
            >
              {{ data.desvio_porcentaje > 0 ? '+' : '' }}{{ data.desvio_porcentaje }}%
            </span>
          </template>
        </Column>

        <Column header="Estado Auditoría" style="width: 140px">
          <template #body="{ data }">
            <span v-if="data.alerta" class="flex items-center gap-1 text-rose-600 font-bold text-[11px]">
              <i class="pi pi-exclamation-triangle"></i> Desvío Crítico
            </span>
            <span v-else class="flex items-center gap-1 text-brand-600 font-medium text-[11px]">
              <i class="pi pi-check-circle"></i> Dentro de Norma
            </span>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { apiClient } from '@/services/api';

const toast = useToast();
const loading = ref(false);
const mes = ref(new Date().getMonth() + 1);
const anio = ref(new Date().getFullYear());
const conciliacionItems = ref<any[]>([]);

const getNombreMes = (m: number) => {
  const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  return meses[m - 1] || '';
};

const formatCurrency = (val: number) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const cargarConciliacion = async () => {
  loading.value = true;
  try {
    const res = await apiClient.get('/produccion/conciliacion', {
      params: { mes: mes.value, anio: anio.value }
    });
    conciliacionItems.value = res.data;
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al consultar conciliación', life: 3000 });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  cargarConciliacion();
});
</script>
