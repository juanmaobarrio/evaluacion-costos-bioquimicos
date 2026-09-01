<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight text-white">Simulador de Escenarios "¿Qué pasa si?"</h1>
        <p class="text-sm text-slate-400">Análisis de sensibilidad y estrés financiero ante variaciones macroeconómicas o de volumen</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="resetearEscenario" class="btn-secondary text-xs">
          <i class="pi pi-undo"></i>
          <span>Restablecer Parámetros</span>
        </button>
        <button @click="ejecutarSimulacion" :disabled="loading" class="btn-primary text-xs">
          <i class="pi pi-sliders-h" :class="{ 'pi-spin': loading }"></i>
          <span>Calcular Simulación</span>
        </button>
      </div>
    </div>

    <!-- Sliders and Inputs Panel -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-2">
        <i class="pi pi-cog text-emerald-400"></i>
        Variables y Palancas de Estrés Financiero
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- 1. Variación USD -->
        <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
          <div class="flex justify-between items-center text-xs">
            <span class="font-semibold text-slate-200">Devaluación USD</span>
            <span class="font-bold font-mono" :class="params.variacion_usd_porcentaje > 0 ? 'text-amber-400' : 'text-slate-400'">
              {{ params.variacion_usd_porcentaje > 0 ? '+' : '' }}{{ params.variacion_usd_porcentaje }}%
            </span>
          </div>
          <Slider v-model="params.variacion_usd_porcentaje" :min="-50" :max="150" :step="5" class="w-full" />
          <p class="text-[10px] text-slate-500">Impacta en reactivos cotizados en moneda extranjera</p>
        </div>

        <!-- 2. Variación Reactivos -->
        <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
          <div class="flex justify-between items-center text-xs">
            <span class="font-semibold text-slate-200">Inflación Reactivos</span>
            <span class="font-bold font-mono" :class="params.variacion_reactivos_porcentaje > 0 ? 'text-rose-400' : 'text-slate-400'">
              {{ params.variacion_reactivos_porcentaje > 0 ? '+' : '' }}{{ params.variacion_reactivos_porcentaje }}%
            </span>
          </div>
          <Slider v-model="params.variacion_reactivos_porcentaje" :min="-30" :max="100" :step="5" class="w-full" />
          <p class="text-[10px] text-slate-500">Aumento directo de proveedores de kits e insumos</p>
        </div>

        <!-- 3. Variación Gastos Fijos -->
        <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
          <div class="flex justify-between items-center text-xs">
            <span class="font-semibold text-slate-200">Suba Gastos Fijos</span>
            <span class="font-bold font-mono" :class="params.variacion_fijos_porcentaje > 0 ? 'text-rose-400' : 'text-slate-400'">
              {{ params.variacion_fijos_porcentaje > 0 ? '+' : '' }}{{ params.variacion_fijos_porcentaje }}%
            </span>
          </div>
          <Slider v-model="params.variacion_fijos_porcentaje" :min="-30" :max="100" :step="5" class="w-full" />
          <p class="text-[10px] text-slate-500">Aumento en alquileres, servicios o sueldos</p>
        </div>

        <!-- 4. Variación Volumen de Pacientes -->
        <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
          <div class="flex justify-between items-center text-xs">
            <span class="font-semibold text-slate-200">Volumen Pacientes</span>
            <span class="font-bold font-mono" :class="params.variacion_volumen_pacientes_porcentaje < 0 ? 'text-rose-400' : 'text-emerald-400'">
              {{ params.variacion_volumen_pacientes_porcentaje > 0 ? '+' : '' }}{{ params.variacion_volumen_pacientes_porcentaje }}%
            </span>
          </div>
          <Slider v-model="params.variacion_volumen_pacientes_porcentaje" :min="-70" :max="100" :step="5" class="w-full" />
          <p class="text-[10px] text-slate-500">Afecta la dilución del overhead por paciente</p>
        </div>
      </div>
    </div>

    <!-- Simulation Results Summary -->
    <div v-if="resultado" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card-stat">
        <div class="text-xs text-slate-400 uppercase font-semibold">Gastos Fijos Simulados</div>
        <div class="text-2xl font-bold text-sky-400 mt-1">
          ${{ formatCurrency(resultado.gastos_fijos_simulados) }}
        </div>
        <div class="text-xs text-slate-500 mt-1">
          Estructura mensual proyectada
        </div>
      </div>

      <div class="card-stat">
        <div class="text-xs text-slate-400 uppercase font-semibold">Pacientes Mensuales Proyectados</div>
        <div class="text-2xl font-bold text-white mt-1">
          {{ resultado.volumen_pacientes_simulado }} pacientes
        </div>
        <div class="text-xs text-slate-500 mt-1">
          Volumen mensual recalculado
        </div>
      </div>

      <div class="card-stat">
        <div class="text-xs text-slate-400 uppercase font-semibold">Nuevo Overhead Unitario</div>
        <div class="text-2xl font-bold mt-1" :class="resultado.delta_overhead_porcentaje > 0 ? 'text-rose-400' : 'text-emerald-400'">
          ${{ formatCurrency(resultado.overhead_por_paciente_simulado) }}
        </div>
        <div class="text-xs text-slate-500 mt-1">
          Impacto: {{ resultado.delta_overhead_porcentaje > 0 ? '+' : '' }}{{ resultado.delta_overhead_porcentaje }}% vs base (${{ formatCurrency(resultado.overhead_por_paciente_base) }})
        </div>
      </div>
    </div>

    <!-- Simulation Detailed Table -->
    <div v-if="resultado" class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider">
        Impacto Unitario en Todas las Determinaciones
      </h3>

      <DataTable :value="resultado.determinaciones" :paginator="true" :rows="10" class="text-xs">
        <Column field="codigo" header="Código" style="width: 100px">
          <template #body="{ data }">
            <span class="font-mono text-emerald-400 font-semibold">{{ data.codigo || '-' }}</span>
          </template>
        </Column>

        <Column field="nombre" header="Determinación" />

        <Column field="costo_original" header="Costo Base">
          <template #body="{ data }">
            <span class="text-slate-400">${{ formatCurrency(data.costo_original) }}</span>
          </template>
        </Column>

        <Column field="costo_simulado" header="Costo Simulado">
          <template #body="{ data }">
            <span class="font-bold text-rose-400">${{ formatCurrency(data.costo_simulado) }}</span>
          </template>
        </Column>

        <Column field="delta_porcentaje" header="Variación Costo">
          <template #body="{ data }">
            <span class="font-semibold font-mono" :class="data.delta_porcentaje > 0 ? 'text-rose-400' : 'text-emerald-400'">
              {{ data.delta_porcentaje > 0 ? '+' : '' }}{{ data.delta_porcentaje }}%
            </span>
          </template>
        </Column>

        <Column field="arancel_referencia" header="Arancel Ref.">
          <template #body="{ data }">
            <span class="text-slate-300">${{ formatCurrency(data.arancel_referencia) }}</span>
          </template>
        </Column>

        <Column field="nuevo_margen_porcentaje" header="Margen Simulado">
          <template #body="{ data }">
            <span
              class="px-2 py-0.5 rounded-full font-bold text-[11px]"
              :class="data.nuevo_margen_porcentaje < 40 ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-emerald-950 text-emerald-400 border border-emerald-800'"
            >
              {{ data.nuevo_margen_porcentaje }}%
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
const resultado = ref<any>(null);

const params = ref({
  variacion_usd_porcentaje: 20,
  variacion_reactivos_porcentaje: 15,
  variacion_fijos_porcentaje: 10,
  variacion_volumen_pacientes_porcentaje: -10
});

const formatCurrency = (val: number) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const ejecutarSimulacion = async () => {
  loading.value = true;
  try {
    const response = await apiClient.post('/costos/simular', params.value);
    resultado.value = response.data;
    toast.add({ severity: 'success', summary: 'Simulado', detail: 'Escenario simulado con éxito', life: 2500 });
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al simular escenario', life: 3000 });
  } finally {
    loading.value = false;
  }
};

const resetearEscenario = () => {
  params.value = {
    variacion_usd_porcentaje: 0,
    variacion_reactivos_porcentaje: 0,
    variacion_fijos_porcentaje: 0,
    variacion_volumen_pacientes_porcentaje: 0
  };
  ejecutarSimulacion();
};

onMounted(() => {
  ejecutarSimulacion();
});
</script>
