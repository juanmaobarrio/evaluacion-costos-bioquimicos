<template>
  <div class="flex h-screen bg-slate-50 overflow-hidden">
    <!-- Sidebar -->
    <aside
      class="relative bg-brand-900 border-r border-brand-800 flex flex-col justify-between shrink-0 transition-[width] duration-300 ease-in-out"
      :class="collapsed ? 'w-[72px]' : 'w-64'"
    >
      <!-- Toggle Button -->
      <button
        @click="toggleSidebar"
        :title="collapsed ? 'Expandir menú' : 'Colapsar menú'"
        :aria-label="collapsed ? 'Expandir menú' : 'Colapsar menú'"
        class="absolute -right-3 top-7 z-10 w-6 h-6 rounded-full bg-white border border-slate-300 text-brand-700 hover:text-white hover:bg-brand-600 hover:border-brand-600 flex items-center justify-center shadow-md transition-colors"
      >
        <i class="pi text-[10px]" :class="collapsed ? 'pi-chevron-right' : 'pi-chevron-left'"></i>
      </button>

      <div class="overflow-hidden">
        <!-- Logo & Title -->
        <div class="h-[81px] border-b border-brand-800 flex items-center gap-3 overflow-hidden" :class="collapsed ? 'justify-center px-0' : 'px-5'">
          <div class="w-10 h-10 shrink-0 rounded-xl bg-gradient-to-tr from-brand-500 to-brand-300 flex items-center justify-center shadow-md shadow-brand-950/40">
            <i class="pi pi-chart-line text-white text-xl"></i>
          </div>
          <div v-show="!collapsed" class="whitespace-nowrap">
            <h1 class="font-bold text-base tracking-wide text-white">BioCostos</h1>
            <p class="text-xs text-brand-300">Auditoría Bioquímica</p>
          </div>
        </div>

        <!-- Navigation Links -->
        <nav class="p-3 space-y-1">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            :title="collapsed ? item.label : undefined"
            class="flex items-center gap-3 py-2.5 rounded-xl font-medium text-sm transition-all group"
            :class="[
              collapsed ? 'justify-center px-0' : 'px-3.5',
              $route.path === item.path
                ? 'bg-brand-600 text-white shadow-md shadow-brand-950/40'
                : 'text-brand-200 hover:text-white hover:bg-brand-800'
            ]"
          >
            <i :class="[item.icon, 'text-base shrink-0 group-hover:scale-110 transition-transform']"></i>
            <span v-show="!collapsed" class="whitespace-nowrap truncate">{{ item.label }}</span>
          </router-link>
        </nav>
      </div>

      <!-- Bottom User Card -->
      <div class="border-t border-brand-800 bg-brand-950/40" :class="collapsed ? 'p-3' : 'p-4'">
        <div class="flex items-center gap-2" :class="collapsed ? 'flex-col' : 'justify-between'">
          <div class="flex items-center gap-3 overflow-hidden">
            <div
              class="w-9 h-9 shrink-0 rounded-full bg-brand-800 border border-brand-700 flex items-center justify-center text-white font-bold"
              :title="collapsed ? `${authStore.user?.full_name || 'Usuario'} (${authStore.user?.role || 'Consulta'})` : undefined"
            >
              {{ authStore.user?.full_name?.charAt(0) || 'U' }}
            </div>
            <div v-show="!collapsed" class="truncate">
              <p class="text-xs font-semibold text-white truncate">{{ authStore.user?.full_name || 'Usuario' }}</p>
              <span class="inline-block text-[10px] px-1.5 py-0.5 rounded uppercase font-bold tracking-wider bg-brand-800 text-brand-200 border border-brand-700">
                {{ authStore.user?.role || 'Consulta' }}
              </span>
            </div>
          </div>
          <button
            @click="handleLogout"
            title="Cerrar sesión"
            class="p-2 text-brand-300 hover:text-rose-300 hover:bg-brand-800 rounded-lg transition-colors"
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
        class="h-16 bg-white backdrop-blur-md border-b border-slate-200 px-6 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <h2 class="text-lg font-bold text-slate-900 capitalize">{{ currentRouteTitle }}</h2>
        </div>
        <div class="flex items-center gap-4">
          <!-- TC Button / Dialog trigger -->
          <button
            @click="openTcDialog"
            title="Hacé clic para modificar la tasa de cambio de referencia"
            class="flex items-center gap-2 px-3 py-1.5 bg-brand-50 hover:bg-brand-100 border border-brand-200 hover:border-brand-400 rounded-lg text-xs transition-all cursor-pointer group"
          >
            <i class="pi pi-dollar text-brand-600 group-hover:scale-110 transition-transform"></i>
            <span class="text-slate-500">TC Referencia:</span>
            <span class="font-bold text-brand-600">${{ formatCurrency(tcValue) }} ARS/USD</span>
            <i class="pi pi-pencil text-[10px] text-slate-500 group-hover:text-brand-600 ml-1"></i>
          </button>
          <div class="flex items-center gap-2 px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="text-slate-600">Motor de Cálculo: Activo</span>
          </div>
        </div>
      </header>

      <!-- Modal Rápido Tipo de Cambio -->
      <Dialog v-model:visible="tcDialog" modal header="Tasa de Cambio de Referencia (USD / ARS)" :style="{ width: '420px' }">
        <form @submit.prevent="saveTc" class="space-y-4 text-xs">
          <p class="text-slate-500">
            Esta tasa se utiliza como valor por defecto para costear insumos cotizados en dólares y calcular márgenes.
          </p>
          <div>
            <label class="block font-semibold text-slate-800 mb-1">Cotización Oficial de Referencia (ARS) *</label>
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 font-bold text-brand-600 text-sm pointer-events-none">$</span>
              <input
                v-model.number="tempTc"
                type="number"
                step="1"
                min="1"
                required
                class="form-input !pl-10 font-mono font-bold text-sm text-brand-600"
                placeholder="1200"
              />
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-3 border-t border-slate-200">
            <button type="button" @click="tcDialog = false" class="btn-secondary text-xs">Cancelar</button>
            <button type="submit" :disabled="savingTc" class="btn-primary text-xs">
              <i class="pi pi-check" :class="{ 'pi-spin': savingTc }"></i>
              <span>Guardar Tasa</span>
            </button>
          </div>
        </form>
      </Dialog>

      <!-- Scrollable View Body -->
      <main class="flex-1 overflow-y-auto p-6 bg-slate-50">
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

// Sidebar colapsable (estado persistido en localStorage)
const SIDEBAR_KEY = 'biocostos_sidebar_collapsed';
const collapsed = ref<boolean>(localStorage.getItem(SIDEBAR_KEY) === '1');

const toggleSidebar = () => {
  collapsed.value = !collapsed.value;
  localStorage.setItem(SIDEBAR_KEY, collapsed.value ? '1' : '0');
};

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
