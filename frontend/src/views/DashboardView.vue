<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight text-slate-900">Dashboard Financiero y Costos</h1>
        <p class="text-sm text-slate-500">Resumen integral de costos operativos, overhead y márgenes por determinación</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="loadData" class="btn-secondary text-xs">
          <i class="pi pi-refresh" :class="{ 'pi-spin': loading }"></i>
          <span>Actualizar Datos</span>
        </button>
      </div>
    </div>

    <!-- Stat Cards Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card-stat">
        <div class="flex items-center justify-between text-slate-500 mb-2">
          <span class="text-xs font-semibold uppercase tracking-wider">Determinaciones</span>
          <i class="pi pi-list text-brand-600"></i>
        </div>
        <div class="text-2xl font-bold text-slate-900">{{ stats.total_determinaciones || 0 }}</div>
        <div class="text-xs text-slate-500 mt-1">Prácticas activas costeadas</div>
      </div>

      <div class="card-stat">
        <div class="flex items-center justify-between text-slate-500 mb-2">
          <span class="text-xs font-semibold uppercase tracking-wider">Autoanalizadores</span>
          <i class="pi pi-server text-brand-400"></i>
        </div>
        <div class="text-2xl font-bold text-slate-900">{{ stats.total_equipos || 0 }}</div>
        <div class="text-xs text-slate-500 mt-1">Equipos con prorrateo</div>
      </div>

      <div class="card-stat">
        <div class="flex items-center justify-between text-slate-500 mb-2">
          <span class="text-xs font-semibold uppercase tracking-wider">Gastos Fijos Mensuales</span>
          <i class="pi pi-building text-sky-600"></i>
        </div>
        <div class="text-2xl font-bold text-sky-600">
          ${{ formatCurrency(stats.total_gastos_fijos_mensuales || 0) }}
        </div>
        <div class="text-xs text-slate-500 mt-1">Overhead estructural del laboratorio</div>
      </div>

      <div class="card-stat">
        <div class="flex items-center justify-between text-slate-500 mb-2">
          <span class="text-xs font-semibold uppercase tracking-wider">Overhead por Paciente</span>
          <i class="pi pi-user text-amber-600"></i>
        </div>
        <div class="text-2xl font-bold text-amber-600">
          ${{ formatCurrency(stats.overhead_promedio_por_paciente || 0) }}
        </div>
        <div class="text-xs text-slate-500 mt-1">Base {{ stats.volumen_pacientes_estimado || 1500 }} pacientes/mes</div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Gastos Fijos Por Categoría -->
      <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xl">
        <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 flex items-center gap-2">
          <i class="pi pi-chart-pie text-brand-600"></i>
          Distribución de Gastos Fijos (Overhead)
        </h3>
        <div class="h-64 flex items-center justify-center">
          <canvas id="gastosChart"></canvas>
        </div>
      </div>

      <!-- Costo Promedio por Sección -->
      <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xl">
        <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 flex items-center gap-2">
          <i class="pi pi-chart-bar text-sky-600"></i>
          Costo Promedio por Sección de Laboratorio
        </h3>
        <div class="h-64 flex items-center justify-center">
          <canvas id="seccionChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Tables: Top Costosas vs Menor Margen -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Top Costosas -->
      <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xl">
        <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 flex items-center gap-2">
          <i class="pi pi-sort-amount-down text-rose-600"></i>
          Top 5 Determinaciones de Mayor Costo
        </h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="text-slate-500 border-b border-slate-200 pb-2">
                <th class="pb-2">Estudio</th>
                <th class="pb-2">Sección</th>
                <th class="pb-2 text-right">Costo Unitario</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200/60">
              <tr v-for="item in stats.top_mas_costosas" :key="item.nombre" class="hover:bg-slate-100">
                <td class="py-2.5 font-medium text-slate-800">{{ item.nombre }}</td>
                <td class="py-2.5 text-slate-500">{{ item.seccion }}</td>
                <td class="py-2.5 text-right font-bold text-rose-600">${{ formatCurrency(item.costo) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Menor Margen -->
      <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-xl">
        <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 flex items-center gap-2">
          <i class="pi pi-exclamation-triangle text-amber-600"></i>
          Determinaciones con Menor Margen (%)
        </h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="text-slate-500 border-b border-slate-200 pb-2">
                <th class="pb-2">Estudio</th>
                <th class="pb-2 text-right">Costo</th>
                <th class="pb-2 text-right">Arancel</th>
                <th class="pb-2 text-right">Margen</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200/60">
              <tr v-for="item in stats.top_menor_margen" :key="item.nombre" class="hover:bg-slate-100">
                <td class="py-2.5 font-medium text-slate-800">{{ item.nombre }}</td>
                <td class="py-2.5 text-right text-slate-500">${{ formatCurrency(item.costo) }}</td>
                <td class="py-2.5 text-right font-semibold text-slate-800">${{ formatCurrency(item.arancel) }}</td>
                <td class="py-2.5 text-right font-bold" :class="item.margen_pct < 50 ? 'text-rose-600' : 'text-amber-600'">
                  {{ item.margen_pct.toFixed(1) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
import { apiClient } from '@/services/api';

Chart.register(...registerables);

const loading = ref(false);
const stats = ref<any>({});
let gastosChartInstance: any = null;
let seccionChartInstance: any = null;

const formatCurrency = (val: number) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const renderCharts = () => {
  if (gastosChartInstance) gastosChartInstance.destroy();
  if (seccionChartInstance) seccionChartInstance.destroy();

  // 1. Gastos Fijos Doughnut
  const ctxGastos = (document.getElementById('gastosChart') as HTMLCanvasElement)?.getContext('2d');
  if (ctxGastos && stats.value.distribucion_gastos_fijos) {
    const labels = stats.value.distribucion_gastos_fijos.map((d: any) => d.categoria);
    const data = stats.value.distribucion_gastos_fijos.map((d: any) => d.monto);

    gastosChartInstance = new Chart(ctxGastos, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: ['#10b981', '#38bdf8', '#f59e0b', '#ec4899', '#8b5cf6', '#64748b'],
          borderColor: '#0f172a',
          borderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { color: '#cbd5e1', font: { size: 11 } } }
        }
      }
    });
  }

  // 2. Costo Promedio por Sección Bar
  const ctxSeccion = (document.getElementById('seccionChart') as HTMLCanvasElement)?.getContext('2d');
  if (ctxSeccion && stats.value.costo_promedio_por_seccion) {
    const labels = stats.value.costo_promedio_por_seccion.map((d: any) => d.seccion);
    const data = stats.value.costo_promedio_por_seccion.map((d: any) => d.costo_promedio);

    seccionChartInstance = new Chart(ctxSeccion, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Costo Promedio (ARS)',
          data,
          backgroundColor: '#38bdf8',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
          y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
        }
      }
    });
  }
};

const loadData = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/costos/dashboard-resumen');
    stats.value = response.data;
    await nextTick();
    renderCharts();
  } catch (err) {
    console.error('Error loading dashboard stats', err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadData();
});
</script>
