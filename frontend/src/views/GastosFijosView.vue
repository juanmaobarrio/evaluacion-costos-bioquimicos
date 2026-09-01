<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight text-white">Gastos Fijos y Parámetros Operativos</h1>
        <p class="text-sm text-slate-400">Estructura fija mensual (Overhead), parámetros de costeo y kit de extracción</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="openNewGastoDialog" class="btn-primary text-xs">
          <i class="pi pi-plus"></i>
          <span>Nuevo Gasto Fijo</span>
        </button>
      </div>
    </div>

    <!-- Tabs Container -->
    <TabView class="bg-slate-900 border border-slate-800 rounded-2xl p-2 shadow-xl">
      <!-- TAB 1: GASTOS FIJOS MENSUALES -->
      <TabPanel header="Gastos Fijos Mensuales (Overhead)">
        <div class="p-2 space-y-4">
          <div class="flex justify-between items-center p-4 bg-slate-950 rounded-xl border border-slate-800">
            <div>
              <div class="text-xs text-slate-400">Total Gastos Fijos Mensuales Activos</div>
              <div class="text-2xl font-bold text-sky-400">${{ formatCurrency(totalGastosFijos) }}</div>
            </div>
            <div class="text-right">
              <div class="text-xs text-slate-400">Overhead por Paciente (Base {{ pacientesEstimados }} pac/mes)</div>
              <div class="text-xl font-bold text-emerald-400">${{ formatCurrency(overheadPorPaciente) }}</div>
            </div>
          </div>

          <DataTable :value="gastosFijos" :loading="loading" class="text-xs">
            <Column field="concepto" header="Concepto / Gasto" :sortable="true">
              <template #body="{ data }">
                <span class="font-semibold text-slate-100">{{ data.concepto }}</span>
              </template>
            </Column>
            <Column field="categoria" header="Categoría" :sortable="true">
              <template #body="{ data }">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-300 border border-slate-700">
                  {{ data.categoria }}
                </span>
              </template>
            </Column>
            <Column field="monto_mensual" header="Monto Mensual (ARS)" :sortable="true">
              <template #body="{ data }">
                <span class="font-bold text-slate-100">${{ formatCurrency(data.monto_mensual) }}</span>
              </template>
            </Column>
            <Column header="Acciones" style="width: 100px">
              <template #body="{ data }">
                <div class="flex items-center gap-2">
                  <button @click="editGasto(data)" class="p-1.5 text-slate-400 hover:text-emerald-400 rounded">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button @click="deleteGasto(data)" class="p-1.5 text-slate-400 hover:text-rose-400 rounded">
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </TabPanel>

      <!-- TAB 2: KIT DE EXTRACCIÓN POR PACIENTE -->
      <TabPanel header="Material Descartable de Extracción">
        <div class="p-2 space-y-4">
          <div class="flex justify-between items-center">
            <div>
              <p class="text-xs text-slate-400">Materiales estándar computados en cada toma de muestra / atención de paciente</p>
              <p class="text-sm font-bold text-emerald-400 mt-1">Costo Total Kit: ${{ formatCurrency(costoKitExtraccion) }}</p>
            </div>
            <button @click="openAddMaterialDialog" class="btn-secondary text-xs">
              <i class="pi pi-plus"></i>
              <span>Agregar Insumo al Kit</span>
            </button>
          </div>

          <DataTable :value="materialesExtraccion" class="text-xs">
            <Column header="Insumo / Descartable">
              <template #body="{ data }">
                <div class="font-semibold text-slate-100">{{ data.insumo?.nombre }}</div>
                <div class="text-[10px] text-slate-400">{{ data.insumo?.marca_proveedor }}</div>
              </template>
            </Column>
            <Column field="cantidad" header="Cantidad por Paciente" style="width: 160px">
              <template #body="{ data }">
                <span>{{ data.cantidad }} {{ data.insumo?.unidad_medida }}</span>
              </template>
            </Column>
            <Column header="Costo Unitario">
              <template #body="{ data }">
                <span>${{ formatCurrency(data.insumo?.costo_unitario_ars) }}</span>
              </template>
            </Column>
            <Column field="costo_subtotal_ars" header="Subtotal">
              <template #body="{ data }">
                <span class="font-bold text-slate-200">${{ formatCurrency(data.costo_subtotal_ars) }}</span>
              </template>
            </Column>
            <Column header="Acciones" style="width: 80px">
              <template #body="{ data }">
                <button @click="deleteMaterial(data)" class="p-1.5 text-rose-400 hover:bg-slate-800 rounded">
                  <i class="pi pi-trash"></i>
                </button>
              </template>
            </Column>
          </DataTable>
        </div>
      </TabPanel>

      <!-- TAB 3: PARÁMETROS OPERATIVOS -->
      <TabPanel header="Parámetros del Laboratorio">
        <div class="p-2 space-y-4 max-w-2xl">
          <div v-for="param in parametros" :key="param.id" class="p-4 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between">
            <div>
              <div class="font-bold text-slate-200 text-xs">{{ param.clave }}</div>
              <div class="text-[11px] text-slate-400 mt-0.5">{{ param.descripcion }}</div>
            </div>
            <div class="flex items-center gap-2">
              <input
                v-model.number="param.valor_numerico"
                type="number"
                class="form-input text-xs w-36 text-right font-mono font-bold"
              />
              <button @click="updateParametro(param)" class="btn-primary text-xs px-3 py-1.5">
                <i class="pi pi-check"></i>
              </button>
            </div>
          </div>
        </div>
      </TabPanel>
    </TabView>

    <!-- Dialog Gasto Fijo -->
    <Dialog v-model:visible="gastoDialog" modal :header="formGasto.id ? 'Editar Gasto Fijo' : 'Nuevo Gasto Fijo'" :style="{ width: '450px' }">
      <form @submit.prevent="saveGasto" class="space-y-4 text-xs">
        <div>
          <label class="block font-semibold text-slate-300 mb-1">Concepto *</label>
          <input v-model="formGasto.concepto" required class="form-input text-xs" placeholder="Ej: Alquiler Sede Central" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Categoría *</label>
            <select v-model="formGasto.categoria" required class="form-input text-xs">
              <option value="Alquileres">Alquileres</option>
              <option value="Sueldos">Sueldos</option>
              <option value="Servicios">Servicios</option>
              <option value="Software">Software</option>
              <option value="Impuestos">Impuestos</option>
              <option value="Otro">Otro</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold text-slate-300 mb-1">Monto Mensual (ARS) *</label>
            <input v-model.number="formGasto.monto_mensual" type="number" step="100" required class="form-input text-xs" />
          </div>
        </div>
        <div class="flex justify-end gap-2 pt-4 border-t border-slate-800">
          <button type="button" @click="gastoDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Guardar</button>
        </div>
      </form>
    </Dialog>

    <!-- Dialog Agregar Insumo Extracción -->
    <Dialog v-model:visible="materialDialog" modal header="Agregar Insumo a Extracción" :style="{ width: '450px' }">
      <form @submit.prevent="saveMaterialExtraccion" class="space-y-4 text-xs">
        <div>
          <label class="block font-semibold text-slate-300 mb-1">Insumo Descartable *</label>
          <select v-model="formMaterial.insumo_id" required class="form-input text-xs">
            <option v-for="ins in insumosDescartables" :key="ins.id" :value="ins.id">
              {{ ins.nombre }} (${{ formatCurrency(ins.costo_unitario_ars) }}/{{ ins.unidad_medida }})
            </option>
          </select>
        </div>
        <div>
          <label class="block font-semibold text-slate-300 mb-1">Cantidad por Paciente *</label>
          <input v-model.number="formMaterial.cantidad" type="number" step="0.5" min="0.1" required class="form-input text-xs" />
        </div>
        <div class="flex justify-end gap-2 pt-4 border-t border-slate-800">
          <button type="button" @click="materialDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Agregar</button>
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { apiClient } from '@/services/api';
import type { GastoFijo, Insumo } from '@/types';

const toast = useToast();

const loading = ref(false);
const gastosFijos = ref<GastoFijo[]>([]);
const materialesExtraccion = ref<any[]>([]);
const parametros = ref<any[]>([]);
const allInsumos = ref<Insumo[]>([]);

const gastoDialog = ref(false);
const formGasto = ref<any>({ id: null, concepto: '', categoria: 'Servicios', monto_mensual: 100000 });

const materialDialog = ref(false);
const formMaterial = ref<any>({ insumo_id: null, cantidad: 1.0 });

const formatCurrency = (val: number) => {
  return Number(val || 0).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const totalGastosFijos = computed(() => {
  return gastosFijos.value.filter((g) => g.activo).reduce((acc, g) => acc + Number(g.monto_mensual || 0), 0);
});

const pacientesEstimados = computed(() => {
  const p = parametros.value.find((x) => x.clave === 'PACIENTES_MENSUALES_ESTIMADOS');
  return p ? Number(p.valor_numerico) : 1500;
});

const overheadPorPaciente = computed(() => {
  const pac = pacientesEstimados.value || 1;
  return totalGastosFijos.value / pac;
});

const costoKitExtraccion = computed(() => {
  return materialesExtraccion.value.reduce((acc, m) => acc + Number(m.costo_subtotal_ars || 0), 0);
});

const insumosDescartables = computed(() => {
  return allInsumos.value.filter((i) => i.tipo === 'descartable_extraccion' || i.tipo === 'otro');
});

const loadData = async () => {
  loading.value = true;
  try {
    const [resGf, resMat, resParam, resIns] = await Promise.all([
      apiClient.get('/gastos-fijos'),
      apiClient.get('/materiales-extraccion'),
      apiClient.get('/parametros'),
      apiClient.get('/insumos')
    ]);
    gastosFijos.value = resGf.data;
    materialesExtraccion.value = resMat.data;
    parametros.value = resParam.data;
    allInsumos.value = resIns.data;
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los datos', life: 3000 });
  } finally {
    loading.value = false;
  }
};

const openNewGastoDialog = () => {
  formGasto.value = { id: null, concepto: '', categoria: 'Servicios', monto_mensual: 100000 };
  gastoDialog.value = true;
};

const editGasto = (g: GastoFijo) => {
  formGasto.value = { ...g };
  gastoDialog.value = true;
};

const saveGasto = async () => {
  try {
    if (formGasto.value.id) {
      await apiClient.put(`/gastos-fijos/${formGasto.value.id}`, formGasto.value);
    } else {
      await apiClient.post('/gastos-fijos', formGasto.value);
    }
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Gasto fijo actualizado', life: 3000 });
    gastoDialog.value = false;
    await loadData();
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo guardar el gasto', life: 3000 });
  }
};

const deleteGasto = async (g: GastoFijo) => {
  try {
    await apiClient.delete(`/gastos-fijos/${g.id}`);
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Gasto fijo eliminado', life: 3000 });
    await loadData();
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar', life: 3000 });
  }
};

const openAddMaterialDialog = () => {
  formMaterial.value = { insumo_id: insumosDescartables.value[0]?.id || null, cantidad: 1.0 };
  materialDialog.value = true;
};

const saveMaterialExtraccion = async () => {
  try {
    await apiClient.post('/materiales-extraccion', formMaterial.value);
    toast.add({ severity: 'success', summary: 'Agregado', detail: 'Insumo agregado al kit de extracción', life: 3000 });
    materialDialog.value = false;
    await loadData();
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo agregar el insumo', life: 3000 });
  }
};

const deleteMaterial = async (m: any) => {
  try {
    await apiClient.delete(`/materiales-extraccion/${m.id}`);
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Insumo quitado del kit', life: 3000 });
    await loadData();
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo quitar el insumo', life: 3000 });
  }
};

const updateParametro = async (param: any) => {
  try {
    await apiClient.put(`/parametros/${param.clave}`, {
      valor_numerico: param.valor_numerico,
      descripcion: param.descripcion,
      categoria: param.categoria
    });
    toast.add({ severity: 'success', summary: 'Actualizado', detail: `Parámetro ${param.clave} actualizado`, life: 3000 });
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el parámetro', life: 3000 });
  }
};

onMounted(() => {
  loadData();
});
</script>
