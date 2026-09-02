<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight text-slate-900">Gastos Fijos y Parámetros Operativos</h1>
        <p class="text-sm text-slate-500">Estructura fija mensual (Overhead), parámetros de costeo y kit de extracción</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="openNewGastoDialog" class="btn-primary text-xs">
          <i class="pi pi-plus"></i>
          <span>Nuevo Gasto Fijo</span>
        </button>
      </div>
    </div>

    <!-- Tabs Container -->
    <TabView class="bg-white border border-slate-200 rounded-2xl p-2 shadow-xl">
      <!-- TAB 1: GASTOS FIJOS MENSUALES -->
      <TabPanel header="Gastos Fijos Mensuales (Overhead)">
        <div class="p-2 space-y-4">
          <div class="flex justify-between items-center p-4 bg-slate-50 rounded-xl border border-slate-200">
            <div>
              <div class="text-xs text-slate-500">Total Gastos Fijos Mensuales Activos</div>
              <div class="text-2xl font-bold text-sky-600">${{ formatCurrency(totalGastosFijos) }}</div>
            </div>
            <div class="text-right">
              <div class="text-xs text-slate-500">Overhead por Paciente (Base {{ pacientesEstimados }} pac/mes)</div>
              <div class="text-xl font-bold text-brand-600">${{ formatCurrency(overheadPorPaciente) }}</div>
            </div>
          </div>

          <DataTable :value="gastosFijos" :loading="loading" class="text-xs">
            <Column field="concepto" header="Concepto / Gasto" :sortable="true">
              <template #body="{ data }">
                <span class="font-semibold text-slate-900">{{ data.concepto }}</span>
              </template>
            </Column>
            <Column field="categoria" header="Categoría" :sortable="true">
              <template #body="{ data }">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-100 text-slate-600 border border-slate-300">
                  {{ data.categoria }}
                </span>
              </template>
            </Column>
            <Column field="monto_mensual" header="Monto Mensual (ARS)" :sortable="true">
              <template #body="{ data }">
                <span class="font-bold text-slate-900">${{ formatCurrency(data.monto_mensual) }}</span>
              </template>
            </Column>
            <Column header="Acciones" style="width: 100px">
              <template #body="{ data }">
                <div class="flex items-center gap-2">
                  <button @click="editGasto(data)" class="p-1.5 text-slate-500 hover:text-brand-600 rounded">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button @click="deleteGasto(data)" class="p-1.5 text-slate-500 hover:text-rose-600 rounded">
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
              <p class="text-xs text-slate-500">Materiales estándar computados en cada toma de muestra / atención de paciente</p>
              <p class="text-sm font-bold text-brand-600 mt-1">Costo Total Kit: ${{ formatCurrency(costoKitExtraccion) }}</p>
            </div>
            <button @click="openAddMaterialDialog" class="btn-secondary text-xs">
              <i class="pi pi-plus"></i>
              <span>Agregar Insumo al Kit</span>
            </button>
          </div>

          <DataTable :value="materialesExtraccion" class="text-xs">
            <Column header="Insumo / Descartable">
              <template #body="{ data }">
                <div class="font-semibold text-slate-900">{{ data.insumo?.nombre }}</div>
                <div class="text-[10px] text-slate-500">{{ data.insumo?.marca_proveedor }}</div>
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
                <span class="font-bold text-slate-800">${{ formatCurrency(data.costo_subtotal_ars) }}</span>
              </template>
            </Column>
            <Column header="Acciones" style="width: 80px">
              <template #body="{ data }">
                <button @click="deleteMaterial(data)" class="p-1.5 text-rose-600 hover:bg-slate-100 rounded">
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
          <div v-for="param in parametros" :key="param.id" class="p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
            <div>
              <div class="font-bold text-slate-800 text-xs">{{ param.clave }}</div>
              <div class="text-[11px] text-slate-500 mt-0.5">{{ param.descripcion }}</div>
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

      <!-- TAB 4: SECCIONES DEL LABORATORIO -->
      <TabPanel header="Secciones del Laboratorio">
        <div class="p-2 space-y-4">
          <div class="flex justify-between items-center">
            <div>
              <p class="text-xs text-slate-500">Maestro de secciones operativas para clasificar determinaciones, autoanalizadores y reportes</p>
              <p class="text-sm font-bold text-brand-600 mt-1">{{ secciones.length }} Secciones Activas</p>
            </div>
            <button @click="openNewSeccionDialog" class="btn-primary text-xs">
              <i class="pi pi-plus"></i>
              <span>Nueva Sección</span>
            </button>
          </div>

          <DataTable :value="secciones" class="text-xs">
            <Column field="nombre" header="Nombre de la Sección" :sortable="true">
              <template #body="{ data }">
                <div class="flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full" :class="getColorCircleClass(data.color)"></span>
                  <span class="font-semibold text-slate-900 text-sm">{{ data.nombre }}</span>
                </div>
              </template>
            </Column>
            <Column field="descripcion" header="Descripción / Alcance">
              <template #body="{ data }">
                <span class="text-slate-500">{{ data.descripcion || 'Sin descripción' }}</span>
              </template>
            </Column>
            <Column field="color" header="Color Identificador" style="width: 140px">
              <template #body="{ data }">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase border" :class="getColorBadgeClass(data.color)">
                  {{ data.color || 'emerald' }}
                </span>
              </template>
            </Column>
            <Column header="Acciones" style="width: 100px">
              <template #body="{ data }">
                <div class="flex items-center gap-2">
                  <button @click="editSeccion(data)" title="Editar" class="p-1.5 text-slate-500 hover:text-brand-600 rounded">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button @click="deleteSeccion(data)" title="Eliminar" class="p-1.5 text-slate-500 hover:text-rose-600 rounded">
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </TabPanel>
    </TabView>

    <!-- Dialog Gasto Fijo -->
    <Dialog v-model:visible="gastoDialog" modal :header="formGasto.id ? 'Editar Gasto Fijo' : 'Nuevo Gasto Fijo'" :style="{ width: '450px' }">
      <form @submit.prevent="saveGasto" class="space-y-4 text-xs">
        <div>
          <label class="block font-semibold text-slate-600 mb-1">Concepto *</label>
          <input v-model="formGasto.concepto" required class="form-input text-xs" placeholder="Ej: Alquiler Sede Central" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Categoría *</label>
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
            <label class="block font-semibold text-slate-600 mb-1">Monto Mensual (ARS) *</label>
            <input v-model.number="formGasto.monto_mensual" type="number" step="any" required class="form-input text-xs" />
          </div>
        </div>
        <div class="flex justify-end gap-2 pt-4 border-t border-slate-200">
          <button type="button" @click="gastoDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Guardar</button>
        </div>
      </form>
    </Dialog>

    <!-- Dialog Agregar Insumo Extracción -->
    <Dialog v-model:visible="materialDialog" modal header="Agregar Insumo a Extracción" :style="{ width: '450px' }">
      <form @submit.prevent="saveMaterialExtraccion" class="space-y-4 text-xs">
        <div>
          <label class="block font-semibold text-slate-600 mb-1">Insumo Descartable *</label>
          <select v-model="formMaterial.insumo_id" required class="form-input text-xs">
            <option v-for="ins in insumosDescartables" :key="ins.id" :value="ins.id">
              {{ ins.nombre }} (${{ formatCurrency(ins.costo_unitario_ars) }}/{{ ins.unidad_medida }})
            </option>
          </select>
        </div>
        <div>
          <label class="block font-semibold text-slate-600 mb-1">Cantidad por Paciente *</label>
          <input v-model.number="formMaterial.cantidad" type="number" step="any" min="0.01" required class="form-input text-xs" />
        </div>
        <div class="flex justify-end gap-2 pt-4 border-t border-slate-200">
          <button type="button" @click="materialDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Agregar</button>
        </div>
      </form>
    </Dialog>

    <!-- Dialog Sección Laboratorio -->
    <Dialog v-model:visible="seccionDialog" modal :header="formSeccion.id ? 'Editar Sección' : 'Nueva Sección del Laboratorio'" :style="{ width: '480px' }">
      <form @submit.prevent="saveSeccion" class="space-y-4 text-xs">
        <div>
          <label class="block font-semibold text-slate-600 mb-1">Nombre de la Sección *</label>
          <input v-model="formSeccion.nombre" required class="form-input text-xs" placeholder="Ej: Toxicología y Monitoreo de Drogas" />
        </div>
        <div>
          <label class="block font-semibold text-slate-600 mb-1">Descripción / Alcance</label>
          <input v-model="formSeccion.descripcion" class="form-input text-xs" placeholder="Ej: Dosajes, drogas terapéuticas y de abuso" />
        </div>
        <div>
          <label class="block font-semibold text-slate-600 mb-1">Color Identificador</label>
          <select v-model="formSeccion.color" class="form-input text-xs">
            <option value="emerald">Verde Esmeralda (Química/General)</option>
            <option value="purple">Púrpura (Hematología)</option>
            <option value="sky">Azul Cielo (Inmunología)</option>
            <option value="amber">Ámbar / Amarillo (Endocrinología)</option>
            <option value="cyan">Cian (Microbiología)</option>
            <option value="indigo">Índigo (Biología Molecular)</option>
            <option value="rose">Rosa / Rojo (Orinas/Urgencias)</option>
            <option value="orange">Naranja (Toxicología)</option>
          </select>
        </div>
        <div class="flex justify-end gap-2 pt-4 border-t border-slate-200">
          <button type="button" @click="seccionDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Guardar Sección</button>
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { apiClient } from '@/services/api';
import type { GastoFijo, Insumo, SeccionLaboratorio } from '@/types';

const toast = useToast();
const confirm = useConfirm();

const loading = ref(false);
const gastosFijos = ref<GastoFijo[]>([]);
const materialesExtraccion = ref<any[]>([]);
const parametros = ref<any[]>([]);
const allInsumos = ref<Insumo[]>([]);
const secciones = ref<SeccionLaboratorio[]>([]);

const gastoDialog = ref(false);
const formGasto = ref<any>({ id: null, concepto: '', categoria: 'Servicios', monto_mensual: 100000 });

const materialDialog = ref(false);
const formMaterial = ref<any>({ insumo_id: null, cantidad: 1.0 });

const seccionDialog = ref(false);
const formSeccion = ref<any>({ id: null, nombre: '', descripcion: '', color: 'emerald' });

const getColorCircleClass = (c: string) => {
  const map: any = {
    emerald: 'bg-brand-500',
    purple: 'bg-purple-500',
    sky: 'bg-sky-500',
    amber: 'bg-amber-500',
    cyan: 'bg-cyan-500',
    indigo: 'bg-indigo-500',
    rose: 'bg-rose-500',
    orange: 'bg-orange-500'
  };
  return map[c] || 'bg-brand-500';
};

const getColorBadgeClass = (c: string) => {
  const map: any = {
    emerald: 'bg-brand-50 text-brand-600 border-brand-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    sky: 'bg-sky-50 text-sky-600 border-sky-200',
    amber: 'bg-amber-50 text-amber-600 border-amber-200',
    cyan: 'bg-cyan-50 text-cyan-600 border-cyan-200',
    indigo: 'bg-indigo-50 text-indigo-600 border-indigo-200',
    rose: 'bg-rose-50 text-rose-600 border-rose-200',
    orange: 'bg-orange-50 text-orange-600 border-orange-200'
  };
  return map[c] || 'bg-slate-100 text-slate-600 border-slate-300';
};

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
    const results = await Promise.allSettled([
      apiClient.get('/gastos-fijos'),
      apiClient.get('/materiales-extraccion'),
      apiClient.get('/parametros'),
      apiClient.get('/insumos'),
      apiClient.get('/secciones')
    ]);
    if (results[0].status === 'fulfilled') gastosFijos.value = results[0].value.data;
    if (results[1].status === 'fulfilled') materialesExtraccion.value = results[1].value.data;
    if (results[2].status === 'fulfilled') parametros.value = results[2].value.data;
    if (results[3].status === 'fulfilled') allInsumos.value = results[3].value.data;
    if (results[4].status === 'fulfilled') secciones.value = results[4].value.data;
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar algunos datos', life: 3000 });
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

// --- Secciones Methods ---
const openNewSeccionDialog = () => {
  formSeccion.value = { id: null, nombre: '', descripcion: '', color: 'emerald' };
  seccionDialog.value = true;
};

const editSeccion = (s: SeccionLaboratorio) => {
  formSeccion.value = { ...s };
  seccionDialog.value = true;
};

const saveSeccion = async () => {
  try {
    if (formSeccion.value.id) {
      await apiClient.put(`/secciones/${formSeccion.value.id}`, formSeccion.value);
      toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Sección actualizada correctamente', life: 3000 });
    } else {
      await apiClient.post('/secciones', formSeccion.value);
      toast.add({ severity: 'success', summary: 'Creado', detail: 'Nueva sección registrada', life: 3000 });
    }
    seccionDialog.value = false;
    await loadData();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'No se pudo guardar la sección', life: 3000 });
  }
};

const deleteSeccion = async (s: SeccionLaboratorio) => {
  try {
    await apiClient.delete(`/secciones/${s.id}`);
    toast.add({ severity: 'success', summary: 'Eliminada', detail: `Sección "${s.nombre}" eliminada`, life: 3000 });
    await loadData();
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar la sección', life: 3000 });
  }
};

onMounted(() => {
  loadData();
});
</script>
