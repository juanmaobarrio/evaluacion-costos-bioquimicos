<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight text-slate-900">Protocolos y Costo por Paciente</h1>
        <p class="text-sm text-slate-500">Cálculo integral por orden/atención: Determinaciones + Kit de Extracción + Overhead Fijo</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="openNewDialog" class="btn-primary text-xs">
          <i class="pi pi-plus"></i>
          <span>Nuevo Protocolo / Perfil</span>
        </button>
      </div>
    </div>

    <!-- Header & Search Filter -->
    <div class="flex flex-col sm:flex-row gap-4 justify-between items-center bg-white border border-slate-200 rounded-2xl p-4 shadow-xl">
      <div class="relative w-full sm:w-80">
        <i class="pi pi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-sm"></i>
        <input
          v-model="searchProtoQuery"
          type="text"
          placeholder="Buscar protocolo o perfil por nombre..."
          class="form-input !pl-11 text-xs"
        />
      </div>
      <div class="text-xs text-slate-500 font-medium">
        Mostrando <span class="text-brand-600 font-bold">{{ filteredProtocolos.length }}</span> perfiles / protocolos
      </div>
    </div>

    <!-- Protocols Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="proto in filteredProtocolos"
        :key="proto.id"
        class="bg-white border border-slate-200 hover:border-slate-300 rounded-2xl p-5 shadow-xl transition-all flex flex-col justify-between"
      >
        <div>
          <!-- Top Tag & Code -->
          <div class="flex items-center justify-between mb-2">
            <span class="font-mono text-xs font-bold text-brand-600">{{ proto.codigo || 'PROT' }}</span>
            <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
              {{ proto.estudios.length }} Estudios
            </span>
          </div>

          <h3 class="text-base font-bold text-slate-900 mb-1">{{ proto.nombre }}</h3>
          <p class="text-xs text-slate-500 mb-4 line-clamp-2">{{ proto.descripcion || 'Sin descripción' }}</p>

          <!-- Studies badges -->
          <div class="flex flex-wrap gap-1.5 mb-4">
            <span
              v-for="est in proto.estudios"
              :key="est.id"
              class="text-[11px] px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200"
            >
              {{ est.determinacion?.nombre }}
            </span>
          </div>

          <!-- Cost Breakdown Tree -->
          <div class="space-y-1.5 p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs mb-4">
            <div class="flex justify-between text-slate-500">
              <span>Determinaciones ({{ proto.estudios.length }}):</span>
              <span class="text-slate-800 font-semibold">${{ formatCurrency(proto.costo_determinaciones_ars) }}</span>
            </div>
            <div class="flex justify-between text-slate-500">
              <span>Kit de Extracción / Descartables:</span>
              <span class="text-slate-800 font-semibold">${{ formatCurrency(proto.costo_extraccion_descartables_ars) }}</span>
            </div>
            <div class="flex justify-between text-slate-500">
              <span>Overhead Fijo por Paciente:</span>
              <span class="text-sky-600 font-semibold">${{ formatCurrency(proto.costo_overhead_fijo_ars) }}</span>
            </div>
            <div class="flex justify-between pt-2 border-t border-slate-200 font-bold text-rose-600">
              <span>Costo Total Paciente:</span>
              <span>${{ formatCurrency(proto.costo_total_protocolo_ars) }}</span>
            </div>
          </div>
        </div>

        <!-- Profit & Actions -->
        <div>
          <div class="flex items-center justify-between p-2.5 bg-brand-50/40 rounded-xl border border-brand-100/60 mb-3">
            <div>
              <div class="text-[10px] text-slate-500">Arancel Sugerido</div>
              <div class="text-xs font-bold text-slate-800">${{ formatCurrency(proto.arancel_sugerido_ars) }}</div>
            </div>
            <div class="text-right">
              <div class="text-sm font-black text-emerald-600">{{ proto.margen_estimado_porcentaje }}%</div>
              <div class="text-[10px] text-slate-500">Margen (${{ formatCurrency(proto.margen_bruto_ars) }})</div>
            </div>
          </div>

          <div class="flex items-center justify-end gap-2">
            <button @click="editProtocolo(proto)" class="p-2 text-slate-500 hover:text-brand-600 hover:bg-slate-100 rounded-lg text-xs">
              <i class="pi pi-pencil"></i>
            </button>
            <button @click="confirmDelete(proto)" class="p-2 text-slate-500 hover:text-rose-600 hover:bg-slate-100 rounded-lg text-xs">
              <i class="pi pi-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Dialog Form Protocolo -->
    <Dialog v-model:visible="formDialog" modal :header="formProt.id ? 'Editar Protocolo / Perfil' : 'Nuevo Protocolo / Perfil'" :style="{ width: '680px' }">
      <form @submit.prevent="saveProtocolo" class="space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Nombre Protocolo / Perfil *</label>
            <input v-model="formProt.nombre" required class="form-input text-xs" placeholder="Ej: Perfil Tiroideo Completo" />
          </div>
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Código Interno</label>
            <input v-model="formProt.codigo" class="form-input text-xs" placeholder="Ej: PROT-002" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Descripción / Indicación</label>
            <input v-model="formProt.descripcion" class="form-input text-xs" placeholder="Detalle clínico o administrativo..." />
          </div>
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Arancel Sugerido de Venta (ARS) *</label>
            <input v-model.number="formProt.arancel_sugerido_ars" type="number" step="any" required class="form-input text-xs font-mono font-bold text-brand-600" />
          </div>
        </div>

        <!-- Selección y Buscador de Determinaciones -->
        <div class="pt-2 border-t border-slate-200 space-y-2.5">
          <div class="flex justify-between items-center">
            <div>
              <span class="font-bold text-slate-800 block">Determinaciones que Componen el Perfil</span>
              <span class="text-[10px] text-slate-500">
                Seleccionadas: <strong class="text-brand-600 font-mono">{{ formProt.determinacion_ids.length }}</strong> prácticas
              </span>
            </div>
            <div class="flex items-center gap-2">
              <button type="button" @click="toggleSelectAllFiltered" class="text-[11px] text-sky-600 hover:text-sky-700 font-medium">
                {{ allFilteredSelected ? 'Deseleccionar filtradas' : 'Seleccionar filtradas' }}
              </button>
            </div>
          </div>

          <!-- Barra de Búsqueda y Filtro de Sección dentro del modal -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <div class="sm:col-span-2 relative">
              <i class="pi pi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-xs"></i>
              <input
                v-model="searchDetModalQuery"
                type="text"
                placeholder="Buscar práctica por nombre o código..."
                class="form-input !pl-10 text-xs py-1.5"
              />
            </div>
            <div>
              <select v-model="selectedModalSeccion" class="form-input text-xs py-1.5">
                <option value="">Todas las Secciones</option>
                <option v-for="sec in uniqueSecciones" :key="sec" :value="sec">{{ sec }}</option>
              </select>
            </div>
          </div>

          <!-- Lista Filtrada de Determinaciones con Checkboxes -->
          <div class="max-h-52 overflow-y-auto space-y-1 p-2 bg-slate-50 rounded-xl border border-slate-200">
            <div v-if="filteredModalDeterminaciones.length === 0" class="p-4 text-center text-slate-500">
              No se encontraron determinaciones que coincidan con la búsqueda.
            </div>
            <label
              v-for="det in filteredModalDeterminaciones"
              :key="det.id"
              class="flex items-center gap-2.5 p-2 rounded-lg hover:bg-white cursor-pointer transition-colors border border-transparent"
              :class="{ 'bg-white border-slate-200': formProt.determinacion_ids.includes(det.id) }"
            >
              <input
                type="checkbox"
                :value="det.id"
                v-model="formProt.determinacion_ids"
                class="rounded border-slate-300 text-brand-600 focus:ring-brand-500 bg-white"
              />
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between gap-2">
                  <span class="font-semibold text-slate-800 truncate">{{ det.nombre }}</span>
                  <span class="font-mono text-brand-600 font-bold shrink-0">${{ formatCurrency(det.costo_unitario_total_ars) }}</span>
                </div>
                <div class="flex items-center gap-2 text-[10px] text-slate-500">
                  <span class="font-mono">{{ det.codigo || '-' }}</span> • <span>{{ det.seccion }}</span>
                </div>
              </div>
            </label>
          </div>

          <!-- Resumen de Costo en Vivo del Protocolo -->
          <div class="p-3 bg-white rounded-xl border border-slate-200 space-y-1.5 text-xs">
            <div class="flex justify-between text-slate-500 text-[11px]">
              <span>Costo Determinaciones ({{ formProt.determinacion_ids.length }}):</span>
              <span class="text-slate-800 font-mono font-semibold">${{ formatCurrency(selectedDetsTotalCost) }}</span>
            </div>
            <div class="flex justify-between text-slate-500 text-[11px]">
              <span>Kit Extracción / Descartables:</span>
              <span class="text-slate-800 font-mono font-semibold">${{ formatCurrency(costoExtraccionBase) }}</span>
            </div>
            <div class="flex justify-between text-slate-500 text-[11px]">
              <span>Overhead Fijo por Paciente:</span>
              <span class="text-sky-600 font-mono font-semibold">${{ formatCurrency(overheadBase) }}</span>
            </div>
            <div class="flex justify-between pt-1.5 border-t border-slate-200 font-bold text-rose-600 text-xs">
              <span>Costo Total Estimado Paciente:</span>
              <span class="font-mono text-sm">${{ formatCurrency(selectedDetsTotalCost + costoExtraccionBase + overheadBase) }}</span>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-4 border-t border-slate-200">
          <button type="button" @click="formDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Guardar Protocolo</button>
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
import type { Protocolo, Determinacion } from '@/types';

const toast = useToast();
const confirm = useConfirm();

const loading = ref(false);
const protocolos = ref<Protocolo[]>([]);
const allDeterminaciones = ref<Determinacion[]>([]);
const materialesExtraccion = ref<any[]>([]);
const gastosFijos = ref<any[]>([]);
const parametros = ref<any[]>([]);

const searchProtoQuery = ref('');
const searchDetModalQuery = ref('');
const selectedModalSeccion = ref('');

const formDialog = ref(false);
const formProt = ref<any>({
  id: null,
  nombre: '',
  codigo: '',
  descripcion: '',
  arancel_sugerido_ars: 0,
  determinacion_ids: []
});

const formatCurrency = (val: number | string | undefined | null) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const uniqueSecciones = computed(() => {
  const set = new Set<string>();
  allDeterminaciones.value.forEach((d) => {
    if (d.seccion) set.add(d.seccion);
  });
  return Array.from(set);
});

const filteredProtocolos = computed(() => {
  if (!searchProtoQuery.value) return protocolos.value;
  const q = searchProtoQuery.value.toLowerCase();
  return protocolos.value.filter((p) =>
    p.nombre.toLowerCase().includes(q) ||
    (p.codigo && p.codigo.toLowerCase().includes(q)) ||
    (p.descripcion && p.descripcion.toLowerCase().includes(q))
  );
});

const filteredModalDeterminaciones = computed(() => {
  return allDeterminaciones.value.filter((d) => {
    const matchesSearch = !searchDetModalQuery.value ||
      d.nombre.toLowerCase().includes(searchDetModalQuery.value.toLowerCase()) ||
      (d.codigo && d.codigo.toLowerCase().includes(searchDetModalQuery.value.toLowerCase()));
    const matchesSeccion = !selectedModalSeccion.value || d.seccion === selectedModalSeccion.value;
    return matchesSearch && matchesSeccion;
  });
});

const allFilteredSelected = computed(() => {
  if (filteredModalDeterminaciones.value.length === 0) return false;
  return filteredModalDeterminaciones.value.every((d) => formProt.value.determinacion_ids.includes(d.id));
});

const toggleSelectAllFiltered = () => {
  const filteredIds = filteredModalDeterminaciones.value.map((d) => d.id);
  if (allFilteredSelected.value) {
    // Deseleccionar las filtradas
    formProt.value.determinacion_ids = formProt.value.determinacion_ids.filter(
      (id: number) => !filteredIds.includes(id)
    );
  } else {
    // Agregar todas las filtradas
    const set = new Set([...formProt.value.determinacion_ids, ...filteredIds]);
    formProt.value.determinacion_ids = Array.from(set);
  }
};

const selectedDetsTotalCost = computed(() => {
  const ids = formProt.value.determinacion_ids || [];
  return allDeterminaciones.value
    .filter((d) => ids.includes(d.id))
    .reduce((acc, d) => acc + Number(d.costo_unitario_total_ars || 0), 0);
});

const costoExtraccionBase = computed(() => {
  return materialesExtraccion.value.reduce((acc, m) => acc + Number(m.costo_subtotal_ars || 0), 0);
});

const overheadBase = computed(() => {
  const totalFijo = gastosFijos.value.filter((g) => g.activo).reduce((acc, g) => acc + Number(g.monto_mensual || 0), 0);
  const p = parametros.value.find((x) => x.clave === 'PACIENTES_MENSUALES_ESTIMADOS');
  const pac = p ? Number(p.valor_numerico) : 1500;
  return totalFijo / Math.max(pac, 1);
});

const loadData = async () => {
  loading.value = true;
  try {
    const [resProt, resDet, resMat, resGf, resParam] = await Promise.all([
      apiClient.get('/protocolos'),
      apiClient.get('/determinaciones'),
      apiClient.get('/materiales-extraccion'),
      apiClient.get('/gastos-fijos'),
      apiClient.get('/parametros')
    ]);
    protocolos.value = resProt.data;
    allDeterminaciones.value = resDet.data;
    materialesExtraccion.value = resMat.data;
    gastosFijos.value = resGf.data;
    parametros.value = resParam.data;
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los protocolos', life: 3000 });
  } finally {
    loading.value = false;
  }
};

const openNewDialog = () => {
  formProt.value = {
    id: null,
    nombre: '',
    codigo: '',
    descripcion: '',
    arancel_sugerido_ars: 15000,
    determinacion_ids: []
  };
  searchDetModalQuery.value = '';
  selectedModalSeccion.value = '';
  formDialog.value = true;
};

const editProtocolo = (proto: Protocolo) => {
  formProt.value = {
    id: proto.id,
    nombre: proto.nombre,
    codigo: proto.codigo,
    descripcion: proto.descripcion,
    arancel_sugerido_ars: proto.arancel_sugerido_ars,
    determinacion_ids: (proto.estudios || []).map((e) => e.determinacion_id)
  };
  searchDetModalQuery.value = '';
  selectedModalSeccion.value = '';
  formDialog.value = true;
};

const saveProtocolo = async () => {
  try {
    if (formProt.value.id) {
      await apiClient.put(`/protocolos/${formProt.value.id}`, formProt.value);
      toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Protocolo actualizado', life: 3000 });
    } else {
      await apiClient.post('/protocolos', formProt.value);
      toast.add({ severity: 'success', summary: 'Creado', detail: 'Protocolo creado', life: 3000 });
    }
    formDialog.value = false;
    await loadData();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'Error al guardar', life: 3000 });
  }
};

const confirmDelete = (proto: Protocolo) => {
  confirm.require({
    message: `¿Está seguro de eliminar el protocolo "${proto.nombre}"?`,
    header: 'Confirmar Eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await apiClient.delete(`/protocolos/${proto.id}`);
        toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Protocolo eliminado', life: 3000 });
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
