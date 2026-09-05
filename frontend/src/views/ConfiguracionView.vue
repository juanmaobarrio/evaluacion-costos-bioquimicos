<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-800">Configuración Global del Sistema</h1>
        <p class="text-sm text-slate-500">Gestión de catálogos y valores maestros utilizados en menús desplegables y clasificaciones</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-brand-50 border border-brand-200 text-brand-700 text-xs font-semibold rounded-lg">
          <i class="pi pi-sliders-h text-xs"></i>
          <span>Catálogos Maestros</span>
        </span>
      </div>
    </div>

    <!-- Tabs Container -->
    <TabView class="bg-white border border-slate-200 rounded-2xl p-2 shadow-sm">
      <!-- TAB 1: SECCIONES DEL LABORATORIO -->
      <TabPanel header="Secciones / Departamentos">
        <div class="p-2 space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <p class="text-xs text-slate-500">Departamentos técnicos para clasificación de prácticas analíticas y autoanalizadores</p>
              <p class="text-sm font-bold text-brand-600 mt-0.5">{{ secciones.length }} Secciones Registradas</p>
            </div>
            <button @click="openNewSeccionDialog" class="btn-primary text-xs">
              <i class="pi pi-plus"></i>
              <span>Nueva Sección</span>
            </button>
          </div>

          <DataTable :value="secciones" :loading="loading" class="text-xs">
            <Column field="nombre" header="Nombre de la Sección" :sortable="true">
              <template #body="{ data }">
                <div class="flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full shrink-0" :class="getColorCircleClass(data.color)"></span>
                  <span class="font-semibold text-slate-800 text-sm">{{ data.nombre }}</span>
                </div>
              </template>
            </Column>
            <Column field="descripcion" header="Descripción / Alcance">
              <template #body="{ data }">
                <span class="text-slate-600">{{ data.descripcion || 'Sin descripción' }}</span>
              </template>
            </Column>
            <Column field="color" header="Color" style="width: 140px">
              <template #body="{ data }">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase border" :class="getColorBadgeClass(data.color)">
                  {{ data.color || 'emerald' }}
                </span>
              </template>
            </Column>
            <Column header="Acciones" style="width: 100px">
              <template #body="{ data }">
                <div class="flex items-center gap-1.5">
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

      <!-- TAB 2: TIPOS DE INSUMO -->
      <TabPanel header="Tipos de Insumo">
        <div class="p-2 space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <p class="text-xs text-slate-500">Categorías maestras para reactivos, calibradores, controles, descartables y consumibles</p>
              <p class="text-sm font-bold text-brand-600 mt-0.5">{{ tiposInsumo.length }} Tipos Registrados</p>
            </div>
            <button @click="openNewTipoInsumoDialog" class="btn-primary text-xs">
              <i class="pi pi-plus"></i>
              <span>Nuevo Tipo de Insumo</span>
            </button>
          </div>

          <DataTable :value="tiposInsumo" :loading="loading" class="text-xs">
            <Column field="clave" header="Clave del Sistema" style="width: 160px">
              <template #body="{ data }">
                <span class="font-mono font-bold text-brand-700 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                  {{ data.clave }}
                </span>
              </template>
            </Column>
            <Column field="nombre" header="Nombre del Tipo" :sortable="true">
              <template #body="{ data }">
                <div class="font-semibold text-slate-800">{{ data.nombre }}</div>
                <div class="text-[11px] text-slate-500">{{ data.descripcion }}</div>
              </template>
            </Column>
            <Column field="base_calculo_sugerida" header="Base Sugerida" style="width: 150px">
              <template #body="{ data }">
                <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded border"
                  :class="data.base_calculo_sugerida === 'paciente' ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-slate-100 text-slate-700 border-slate-300'">
                  {{ data.base_calculo_sugerida === 'paciente' ? 'Por Paciente' : 'Por Tests' }}
                </span>
              </template>
            </Column>
            <Column header="Acciones" style="width: 100px">
              <template #body="{ data }">
                <div class="flex items-center gap-1.5">
                  <button @click="editTipoInsumo(data)" title="Editar" class="p-1.5 text-slate-500 hover:text-brand-600 rounded">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button @click="deleteTipoInsumo(data)" title="Eliminar" class="p-1.5 text-slate-500 hover:text-rose-600 rounded">
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </TabPanel>

      <!-- TAB 3: LABORATORIOS DE REFERENCIA -->
      <TabPanel header="Laboratorios de Referencia">
        <div class="p-2 space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <p class="text-xs text-slate-500">Laboratorios externos para derivaciones, contrastación y comparación de costos de outsourced tests</p>
              <p class="text-sm font-bold text-brand-600 mt-0.5">{{ laboratorios.length }} Laboratorios de Referencia</p>
            </div>
            <button @click="openNewLabDialog" class="btn-primary text-xs">
              <i class="pi pi-plus"></i>
              <span>Nuevo Laboratorio</span>
            </button>
          </div>

          <DataTable :value="laboratorios" :loading="loading" class="text-xs">
            <Column field="nombre" header="Laboratorio de Referencia" :sortable="true">
              <template #body="{ data }">
                <div class="font-semibold text-slate-900 text-sm flex items-center gap-1.5">
                  <i class="pi pi-building text-brand-600 text-xs"></i>
                  <span>{{ data.nombre }}</span>
                </div>
                <div class="text-[11px] text-slate-500">{{ data.direccion || 'Sin dirección registrada' }}</div>
              </template>
            </Column>
            <Column header="Contacto y Comunicación">
              <template #body="{ data }">
                <div class="text-slate-700 font-medium">{{ data.contacto || '-' }}</div>
                <div class="text-[11px] text-slate-500 flex items-center gap-2 mt-0.5">
                  <span v-if="data.telefono"><i class="pi pi-phone text-[10px] mr-1"></i>{{ data.telefono }}</span>
                  <span v-if="data.email"><i class="pi pi-envelope text-[10px] mr-1"></i>{{ data.email }}</span>
                </div>
              </template>
            </Column>
            <Column field="notas" header="Especialidad / Notas">
              <template #body="{ data }">
                <span class="text-slate-600 text-[11px]">{{ data.notas || '-' }}</span>
              </template>
            </Column>
            <Column header="Acciones" style="width: 100px">
              <template #body="{ data }">
                <div class="flex items-center gap-1.5">
                  <button @click="editLab(data)" title="Editar" class="p-1.5 text-slate-500 hover:text-brand-600 rounded">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button @click="deleteLab(data)" title="Eliminar" class="p-1.5 text-slate-500 hover:text-rose-600 rounded">
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </TabPanel>
    </TabView>

    <!-- Dialog Sección Laboratorio -->
    <Dialog v-model:visible="seccionDialog" modal :header="formSeccion.id ? 'Editar Sección' : 'Nueva Sección'" :style="{ width: '480px' }">
      <form @submit.prevent="saveSeccion" class="space-y-4 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Nombre de la Sección *</label>
          <input v-model="formSeccion.nombre" required class="form-input text-xs" placeholder="Ej: Toxicología y Monitoreo" />
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Descripción / Alcance</label>
          <input v-model="formSeccion.descripcion" class="form-input text-xs" placeholder="Ej: Dosajes, drogas terapéuticas y de abuso" />
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Color Identificador</label>
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

    <!-- Dialog Tipo de Insumo -->
    <Dialog v-model:visible="tipoDialog" modal :header="formTipo.id ? 'Editar Tipo de Insumo' : 'Nuevo Tipo de Insumo'" :style="{ width: '500px' }">
      <form @submit.prevent="saveTipoInsumo" class="space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Clave Única (slug) *</label>
            <input v-model="formTipo.clave" required class="form-input text-xs font-mono font-bold" placeholder="Ej: medio_cultivo" :disabled="!!formTipo.id" />
            <span class="text-[10px] text-slate-400 mt-0.5 block">Identificador interno en minúsculas</span>
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Nombre Descriptivo *</label>
            <input v-model="formTipo.nombre" required class="form-input text-xs" placeholder="Ej: Medio de Cultivo" />
          </div>
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Descripción</label>
          <input v-model="formTipo.descripcion" class="form-input text-xs" placeholder="Ej: Placas de agar, caldos y medios selectivos" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Base de Cálculo Sugerida *</label>
            <select v-model="formTipo.base_calculo_sugerida" required class="form-input text-xs">
              <option value="test">Por Tests / Determinación</option>
              <option value="paciente">Por Paciente / Extracción</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Color / Badge</label>
            <select v-model="formTipo.color" class="form-input text-xs">
              <option value="brand">Azul Corporativo</option>
              <option value="purple">Púrpura</option>
              <option value="amber">Ámbar</option>
              <option value="cyan">Cian</option>
              <option value="blue">Azul</option>
              <option value="emerald">Verde</option>
              <option value="rose">Rosa / Rojo</option>
              <option value="slate">Gris Neutro</option>
            </select>
          </div>
        </div>
        <div class="flex justify-end gap-2 pt-4 border-t border-slate-200">
          <button type="button" @click="tipoDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Guardar Tipo</button>
        </div>
      </form>
    </Dialog>

    <!-- Dialog Laboratorio de Referencia -->
    <Dialog v-model:visible="labDialog" modal :header="formLab.id ? 'Editar Laboratorio de Referencia' : 'Nuevo Laboratorio de Referencia'" :style="{ width: '540px' }">
      <form @submit.prevent="saveLab" class="space-y-4 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Nombre del Laboratorio *</label>
          <input v-model="formLab.nombre" required class="form-input text-xs font-semibold" placeholder="Ej: Laboratorio Central de Derivaciones" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Contacto / Responsable</label>
            <input v-model="formLab.contacto" class="form-input text-xs" placeholder="Ej: Dr. Juan Pérez" />
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Teléfono</label>
            <input v-model="formLab.telefono" class="form-input text-xs" placeholder="Ej: (011) 4567-8900" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Correo Electrónico</label>
            <input v-model="formLab.email" type="email" class="form-input text-xs" placeholder="derivaciones@labcentral.com" />
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Dirección / Sede</label>
            <input v-model="formLab.direccion" class="form-input text-xs" placeholder="Ej: Av. Corrientes 1234, CABA" />
          </div>
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Notas / Especialidad / Observaciones</label>
          <textarea v-model="formLab.notas" rows="2" class="form-input text-xs" placeholder="Ej: Derivación de pruebas especiales de endocrinología y biología molecular"></textarea>
        </div>
        <div class="flex justify-end gap-2 pt-4 border-t border-slate-200">
          <button type="button" @click="labDialog = false" class="btn-secondary text-xs">Cancelar</button>
          <button type="submit" class="btn-primary text-xs">Guardar Laboratorio</button>
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { configuracionService } from '@/services/configuracion.service';
import type { SeccionLaboratorio, TipoInsumoCatalogo, LaboratorioReferencia } from '@/types';

const toast = useToast();
const confirm = useConfirm();

const loading = ref(false);
const secciones = ref<SeccionLaboratorio[]>([]);
const tiposInsumo = ref<TipoInsumoCatalogo[]>([]);
const laboratorios = ref<LaboratorioReferencia[]>([]);

// Dialogs state
const seccionDialog = ref(false);
const formSeccion = ref<any>({ id: null, nombre: '', descripcion: '', color: 'emerald' });

const tipoDialog = ref(false);
const formTipo = ref<any>({ id: null, clave: '', nombre: '', descripcion: '', color: 'brand', base_calculo_sugerida: 'test', orden: 0 });

const labDialog = ref(false);
const formLab = ref<any>({ id: null, nombre: '', contacto: '', telefono: '', email: '', direccion: '', notas: '' });

const loadAll = async () => {
  loading.value = true;
  try {
    const [sec, tipos, labs] = await Promise.all([
      configuracionService.getSecciones(),
      configuracionService.getTiposInsumo(),
      configuracionService.getLaboratoriosReferencia()
    ]);
    secciones.value = sec;
    tiposInsumo.value = tipos;
    laboratorios.value = labs;
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los catálogos de configuración', life: 3000 });
  } finally {
    loading.value = false;
  }
};

// --- Secciones ---
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
      await configuracionService.updateSeccion(formSeccion.value.id, formSeccion.value);
      toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Sección actualizada correctamente', life: 3000 });
    } else {
      await configuracionService.createSeccion(formSeccion.value);
      toast.add({ severity: 'success', summary: 'Creado', detail: 'Nueva sección registrada', life: 3000 });
    }
    seccionDialog.value = false;
    await loadAll();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'No se pudo guardar la sección', life: 3000 });
  }
};
const deleteSeccion = (s: SeccionLaboratorio) => {
  confirm.require({
    message: `¿Está seguro de eliminar la sección "${s.nombre}"?`,
    header: 'Confirmar Eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await configuracionService.deleteSeccion(s.id);
        toast.add({ severity: 'success', summary: 'Eliminada', detail: `Sección "${s.nombre}" eliminada`, life: 3000 });
        await loadAll();
      } catch (err: any) {
        toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'No se pudo eliminar la sección', life: 3000 });
      }
    }
  });
};

// --- Tipos de Insumo ---
const openNewTipoInsumoDialog = () => {
  formTipo.value = { id: null, clave: '', nombre: '', descripcion: '', color: 'brand', base_calculo_sugerida: 'test', orden: tiposInsumo.value.length + 1 };
  tipoDialog.value = true;
};
const editTipoInsumo = (t: TipoInsumoCatalogo) => {
  formTipo.value = { ...t };
  tipoDialog.value = true;
};
const saveTipoInsumo = async () => {
  try {
    if (formTipo.value.id) {
      await configuracionService.updateTipoInsumo(formTipo.value.id, formTipo.value);
      toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Tipo de insumo actualizado', life: 3000 });
    } else {
      await configuracionService.createTipoInsumo(formTipo.value);
      toast.add({ severity: 'success', summary: 'Creado', detail: 'Nuevo tipo de insumo registrado', life: 3000 });
    }
    tipoDialog.value = false;
    await loadAll();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'No se pudo guardar el tipo', life: 3000 });
  }
};
const deleteTipoInsumo = (t: TipoInsumoCatalogo) => {
  confirm.require({
    message: `¿Está seguro de eliminar el tipo "${t.nombre}"? No se podrá eliminar si existen insumos asociados.`,
    header: 'Confirmar Eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await configuracionService.deleteTipoInsumo(t.id);
        toast.add({ severity: 'success', summary: 'Eliminado', detail: `Tipo "${t.nombre}" eliminado`, life: 3000 });
        await loadAll();
      } catch (err: any) {
        toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'No se pudo eliminar el tipo', life: 3000 });
      }
    }
  });
};

// --- Laboratorios de Referencia ---
const openNewLabDialog = () => {
  formLab.value = { id: null, nombre: '', contacto: '', telefono: '', email: '', direccion: '', notas: '' };
  labDialog.value = true;
};
const editLab = (l: LaboratorioReferencia) => {
  formLab.value = { ...l };
  labDialog.value = true;
};
const saveLab = async () => {
  try {
    if (formLab.value.id) {
      await configuracionService.updateLaboratorioReferencia(formLab.value.id, formLab.value);
      toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Laboratorio de referencia actualizado', life: 3000 });
    } else {
      await configuracionService.createLaboratorioReferencia(formLab.value);
      toast.add({ severity: 'success', summary: 'Creado', detail: 'Nuevo laboratorio de referencia registrado', life: 3000 });
    }
    labDialog.value = false;
    await loadAll();
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'No se pudo guardar el laboratorio', life: 3000 });
  }
};
const deleteLab = (l: LaboratorioReferencia) => {
  confirm.require({
    message: `¿Está seguro de eliminar el laboratorio "${l.nombre}"? No se podrá eliminar si está asociado a determinaciones.`,
    header: 'Confirmar Eliminación',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await configuracionService.deleteLaboratorioReferencia(l.id);
        toast.add({ severity: 'success', summary: 'Eliminado', detail: `Laboratorio "${l.nombre}" eliminado`, life: 3000 });
        await loadAll();
      } catch (err: any) {
        toast.add({ severity: 'error', summary: 'Error', detail: err.response?.data?.detail || 'No se pudo eliminar el laboratorio', life: 3000 });
      }
    }
  });
};

// --- Colores Helpers ---
const getColorCircleClass = (color: string) => {
  const map: any = {
    emerald: 'bg-emerald-500',
    purple: 'bg-purple-500',
    sky: 'bg-sky-500',
    amber: 'bg-amber-500',
    cyan: 'bg-cyan-500',
    indigo: 'bg-indigo-500',
    rose: 'bg-rose-500',
    orange: 'bg-orange-500',
    brand: 'bg-brand-600',
    slate: 'bg-slate-400'
  };
  return map[color] || 'bg-slate-400';
};

const getColorBadgeClass = (color: string) => {
  const map: any = {
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
    sky: 'bg-sky-50 text-sky-700 border-sky-200',
    amber: 'bg-amber-50 text-amber-700 border-amber-200',
    cyan: 'bg-cyan-50 text-cyan-700 border-cyan-200',
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    rose: 'bg-rose-50 text-rose-700 border-rose-200',
    orange: 'bg-orange-50 text-orange-700 border-orange-200',
    brand: 'bg-brand-50 text-brand-700 border-brand-200',
    slate: 'bg-slate-100 text-slate-700 border-slate-300'
  };
  return map[color] || 'bg-slate-100 text-slate-700 border-slate-300';
};

onMounted(() => {
  loadAll();
});
</script>
