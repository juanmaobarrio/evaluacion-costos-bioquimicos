<template>
  <div class="flex h-screen bg-slate-950 overflow-hidden">
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0">
      <div>
        <!-- Logo & Title -->
        <div class="p-5 border-b border-slate-800 flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-950">
            <i class="pi pi-chart-line text-white text-xl"></i>
          </div>
          <div>
            <h1 class="font-bold text-base tracking-wide text-white">BioCostos</h1>
            <p class="text-xs text-slate-400">Auditoría Bioquímica</p>
          </div>
        </div>

        <!-- Navigation Links -->
        <nav class="p-3 space-y-1">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all group"
            :class="[
              $route.path === item.path
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            ]"
          >
            <i :class="[item.icon, 'text-base group-hover:scale-110 transition-transform']"></i>
            <span>{{ item.label }}</span>
          </router-link>
        </nav>
      </div>

      <!-- Bottom User Card -->
      <div class="p-4 border-t border-slate-800 bg-slate-900/50">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3 overflow-hidden">
            <div class="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-emerald-400 font-bold">
              {{ authStore.user?.full_name?.charAt(0) || 'U' }}
            </div>
            <div class="truncate">
              <p class="text-xs font-semibold text-slate-200 truncate">{{ authStore.user?.full_name || 'Usuario' }}</p>
              <span class="inline-block text-[10px] px-1.5 py-0.5 rounded uppercase font-bold tracking-wider bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                {{ authStore.user?.role || 'Consulta' }}
              </span>
            </div>
          </div>
          <button
            @click="handleLogout"
            title="Cerrar sesión"
            class="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <i class="pi pi-sign-out text-lg"></i>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Topbar -->
      <header
        class="h-16 bg-slate-900/70 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <h2 class="text-lg font-bold text-slate-100 capitalize">{{ currentRouteTitle }}</h2>
        </div>
        <div class="flex items-center gap-4">
          <!-- TC Button / Dialog trigger -->
          <button
            @click="openTcDialog"
            title="Hacé clic para modificar la tasa de cambio de referencia"
            class="flex items-center gap-2 px-3 py-1.5 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-emerald-500/50 rounded-lg text-xs transition-all cursor-pointer group"
          >
            <i class="pi pi-dollar text-emerald-400 group-hover:scale-110 transition-transform"></i>
            <span class="text-slate-400">TC Referencia:</span>
            <span class="font-bold text-emerald-400">${{ formatCurrency(tcValue) }} ARS/USD</span>
            <i class="pi pi-pencil text-[10px] text-slate-500 group-hover:text-emerald-400 ml-1"></i>
          </button>
          <div class="flex items-center gap-2 px-3 py-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-xs">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="text-slate-300">Motor de Cálculo: Activo</span>
          </div>
        </div>
      </header>

      <!-- Modal Rápido Tipo de Cambio -->
      <Dialog v-model:visible="tcDialog" modal header="Tasa de Cambio de Referencia (USD / ARS)" :style="{ width: '420px' }">
        <form @submit.prevent="saveTc" class="space-y-4 text-xs">
          <p class="text-slate-400">
            Esta tasa se utiliza como valor por defecto para costear insumos cotizados en dólares y calcular márgenes.
          </p>
          <div>
            <label class="block font-semibold text-slate-200 mb-1">Cotización Oficial de Referencia (ARS) *</label>
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 font-bold text-emerald-400 text-sm pointer-events-none">$</span>
              <input
                v-model.number="tempTc"
                type="number"
                step="1"
                min="1"
                required
                class="form-input !pl-10 font-mono font-bold text-sm text-emerald-400"
                placeholder="1200"
              />
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-3 border-t border-slate-800">
            <button type="button" @click="tcDialog = false" class="btn-secondary text-xs">Cancelar</button>
            <button type="submit" :disabled="savingTc" class="btn-primary text-xs">
              <i class="pi pi-check" :class="{ 'pi-spin': savingTc }"></i>
              <span>Guardar Tasa</span>
            </button>
          </div>
        </form>
      </Dialog>

      <!-- Scrollable View Body -->
      <main class="flex-1 overflow-y-auto p-6 bg-slate-950">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useToast } from 'primevue/usetoast';
import { apiClient } from '@/services/api';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const tcValue = ref<number>(1200);
const tempTc = ref<number>(1200);
const tcDialog = ref(false);
const savingTc = ref(false);

const formatCurrency = (val: number | string | undefined | null) => {
  return Number(val || 0).toLocaleString('es-AR');
};

const loadTc = async () => {
  try {
    const res = await apiClient.get('/parametros');
    const param = res.data.find((p: any) => p.clave === 'USD_EXCHANGE_RATE');
    if (param && param.valor_numerico) {
      tcValue.value = Number(param.valor_numerico);
    }
  } catch (err) {
    // fallback default
  }
};

const openTcDialog = () => {
  tempTc.value = tcValue.value;
  tcDialog.value = true;
};

const saveTc = async () => {
  savingTc.value = true;
  try {
    await apiClient.put('/parametros/USD_EXCHANGE_RATE', {
      valor_numerico: tempTc.value,
      descripcion: 'Tipo de cambio de referencia USD a ARS',
      categoria: 'Moneda'
    });
    tcValue.value = tempTc.value;
    tcDialog.value = false;
    toast.add({
      severity: 'success',
      summary: 'Tipo de Cambio Actualizado',
      detail: `Nueva cotización de referencia: $${Number(tempTc.value).toLocaleString('es-AR')} ARS/USD`,
      life: 3000
    });
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el tipo de cambio', life: 3000 });
  } finally {
    savingTc.value = false;
  }
};

onMounted(() => {
  loadTc();
});

const navItems = [
  { label: 'Dashboard & Finanzas', path: '/', icon: 'pi pi-chart-pie' },
  { label: 'Determinaciones', path: '/determinaciones', icon: 'pi pi-list' },
  { label: 'Insumos y Reactivos', path: '/insumos', icon: 'pi pi-box' },
  { label: 'Equipos y Analizadores', path: '/equipos', icon: 'pi pi-server' },
  { label: 'Protocolos y Pacientes', path: '/protocolos', icon: 'pi pi-users' },
  { label: 'Gastos Fijos (Overhead)', path: '/gastos-fijos', icon: 'pi pi-building' },
  { label: 'Simulador "What-If"', path: '/simulador', icon: 'pi pi-sliders-h' },
  { label: 'Conciliación y Compras', path: '/conciliacion', icon: 'pi pi-sync' },
];

const currentRouteTitle = computed(() => {
  const item = navItems.find((n) => n.path === route.path);
  return item ? item.label : 'Gestión de Costos';
});

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>
