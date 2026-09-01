<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight text-white">Protocolos y Costo por Paciente</h1>
        <p class="text-sm text-slate-400">Cálculo integral por orden/atención: Determinaciones + Kit de Extracción + Overhead Fijo</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="openNewDialog" class="btn-primary text-xs">
          <i class="pi pi-plus"></i>
          <span>Nuevo Protocolo / Perfil</span>
        </button>
      </div>
    </div>

    <!-- Protocols Grid / Table -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="proto in protocolos"
        :key="proto.id"
        class="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 shadow-xl transition-all flex flex-col justify-between"
      >
        <div>
          <!-- Top Tag & Code -->
          <div class="flex items-center justify-between mb-2">
            <span class="font-mono text-xs font-bold text-emerald-400">{{ proto.codigo || 'PROT' }}</span>
            <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
              {{ proto.estudios.length }} Estudios
            </span>
          </div>

          <h3 class="text-base font-bold text-white mb-1">{{ proto.nombre }}</h3>
          <p class="text-xs text-slate-400 mb-4 line-clamp-2">{{ proto.descripcion || 'Sin descripción' }}</p>

          <!-- Studies badges -->
          <div class="flex flex-wrap gap-1.5 mb-4">
            <span
              v-for="est in proto.estudios"
              :key="est.id"
              class="text-[11px] px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/60"
            >
              {{ est.determinacion?.nombre }}
            </span>
          </div>

          <!-- Cost Breakdown Tree -->
          <div class="space-y-1.5 p-3 bg-slate-950 rounded-xl border border-slate-800/80 text-xs mb-4">
            <div class="flex justify-between text-slate-400">
              <span>Determinaciones ({{ proto.estudios.length }}):</span>
              <span class="text-slate-200 font-semibold">${{ formatCurrency(proto.costo_determinaciones_ars) }}</span>
            </div>
            <div class="flex justify-between text-slate-400">
              <span>Kit de Extracción / Descartables:</span>
              <span class="text-slate-200 font-semibold">${{ formatCurrency(proto.costo_extraccion_descartables_ars) }}</span>
            </div>
            <div class="flex justify-between text-slate-400">
              <span>Overhead Fijo por Paciente:</span>
              <span class="text-sky-400 font-semibold">${{ formatCurrency(proto.costo_overhead_fijo_ars) }}</span>
            </div>
            <div class="flex justify-between pt-2 border-t border-slate-800 font-bold text-rose-400">
              <span>Costo Total Paciente:</span>
              <span>${{ formatCurrency(proto.costo_total_protocolo_ars) }}</span>
            </div>
          </div>
        </div>

        <!-- Profit & Actions -->
        <div>
          <div class="flex items-center justify-between p-2.5 bg-emerald-950/40 rounded-xl border border-emerald-900/60 mb-3">
            <div>
              <div class="text-[10px] text-slate-400">Arancel Sugerido</div>
              <div class="text-xs font-bold text-slate-200">${{ formatCurrency(proto.arancel_sugerido_ars) }}</div>
            </div>
            <div class="text-right">
              <div class="text-sm font-black text-emerald-400">{{ proto.margen_estimado_porcentaje }}%</div>
              <div class="text-[10px] text-slate-400">Margen (${{ formatCurrency(proto.margen_bruto_ars) }})</div>
            </div>
          </div>

          <div class="flex items-center justify-end gap-2">
            <button @click="editProtocolo(proto)" class="p-2 text-slate-400 hover:text-emerald-400 hover:bg-slate-800 rounded-lg text-xs">
              <i class="pi pi-pencil"></i>
            </button>
            <button @click="confirmDelete(proto)" class="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg text-xs">
              <i class="pi pi-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Dialog Form Protocolo -->
    <Dialog v-model:visible="formDialog" modal :header="formProt.id ? 'Editar Protocolo' : 'Nuevo Protocolo'" :style="{ width: '600px' }">
      <form @submit.prevent="saveProtocolo" class="space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Nombre Protocolo / Perfil *</label>
            <input v-model="formProt.nombre" required class="form-input text-xs" placeholder="Ej: Perfil Tiroideo Completo" />
          </div>
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Código</label>
            <input v-model="formProt.codigo" class="form-input text-xs" placeholder="Ej: PROT-002" />
          </div>
        </div>

        <div>
          <label class="block font-semibold text-slate-300 mb-1">Descripción</label>
          <textarea v-model="formProt.descripcion" rows="2" class="form-input text-xs" placeholder="Detalle clínico o administrativo..."></textarea>
        </div>

        <div>
          <label class="block font-semibold text-slate-300 mb-1">Arancel Sugerido (ARS)</label>
          <input v-model.number="formProt.arancel_sugerido_ars" type="number" step="any" class="form-input text-xs" />
        </div>

        <!-- Selección de Determinaciones -->
        <div class="pt-2 border-t border-slate-800">
          <label class="block font-bold text-slate-200 mb-2">Seleccionar Determinaciones que componen este protocolo:</label>
          <div class="max-h-48 overflow-y-auto space-y-1.5 p-2 bg-slate-950 rounded-xl border border-slate-800">
            <label
              v-for="det in allDeterminaciones"
              :key="det.id"
              class="flex items-center gap-2.5 p-2 rounded hover:bg-slate-800/60 cursor-pointer transition-colors"
            >
              <input
                type="checkbox"
                :value="det.id"
                v-model="formProt.determinacion_ids"
                class="rounded border-slate-700 text-emerald-600 focus:ring-emerald-500 bg-slate-900"
              />
              <div class="flex-1">
                <div class="font-semibold text-slate-200">{{ det.nombre }}</div>
                <div class="text-[10px] text-slate-400">{{ det.seccion }} • Costo: ${{ formatCurrency(det.costo_unitario_total_ars) }}</div>
              </div>
            </label>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-4 border-t border-slate-800">
          <button type="button" @click="formDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Guardar Protocolo</button>
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import { apiClient } from '@/services/api';
import type { Protocolo, Determinacion } from '@/types';

const toast = useToast();
const confirm = useConfirm();

const loading = ref(false);
const protocolos = ref<Protocolo[]>([]);
const allDeterminaciones = ref<Determinacion[]>([]);

const formDialog = ref(false);
const formProt = ref<any>({
  id: null,
  nombre: '',
  codigo: '',
  descripcion: '',
  arancel_sugerido_ars: 0,
  determinacion_ids: []
});

const formatCurrency = (val: number) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const loadData = async () => {
  loading.value = true;
  try {
    const [resProt, resDet] = await Promise.all([
      apiClient.get('/protocolos'),
      apiClient.get('/determinaciones')
    ]);
    protocolos.value = resProt.data;
    allDeterminaciones.value = resDet.data;
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
  formDialog.value = true;
};

const editProtocolo = (proto: Protocolo) => {
  formProt.value = {
    id: proto.id,
    nombre: proto.nombre,
    codigo: proto.codigo,
    descripcion: proto.descripcion,
    arancel_sugerido_ars: proto.arancel_sugerido_ars,
    determinacion_ids: proto.estudios.map((e) => e.determinacion_id)
  };
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
    message: `¿Está seguro de eliminar el protocolo \"${proto.nombre}\"?`,
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
