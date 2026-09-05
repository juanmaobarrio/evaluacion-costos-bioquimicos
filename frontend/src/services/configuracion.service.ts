import { apiClient } from './api';
import type { SeccionLaboratorio, TipoInsumoCatalogo, LaboratorioReferencia } from '@/types';

export const configuracionService = {
  // Secciones / Departamentos del Laboratorio
  async getSecciones(activoOnly = false): Promise<SeccionLaboratorio[]> {
    const res = await apiClient.get<SeccionLaboratorio[]>('/secciones', { params: { activo_only: activoOnly } });
    return res.data;
  },
  async createSeccion(data: Partial<SeccionLaboratorio>): Promise<SeccionLaboratorio> {
    const res = await apiClient.post<SeccionLaboratorio>('/secciones', data);
    return res.data;
  },
  async updateSeccion(id: number, data: Partial<SeccionLaboratorio>): Promise<SeccionLaboratorio> {
    const res = await apiClient.put<SeccionLaboratorio>(`/secciones/${id}`, data);
    return res.data;
  },
  async deleteSeccion(id: number): Promise<void> {
    await apiClient.delete(`/secciones/${id}`);
  },

  // Tipos de Insumo (Catálogo)
  async getTiposInsumo(activoOnly = false): Promise<TipoInsumoCatalogo[]> {
    const res = await apiClient.get<TipoInsumoCatalogo[]>('/tipos-insumo', { params: { activo_only: activoOnly } });
    return res.data;
  },
  async createTipoInsumo(data: Partial<TipoInsumoCatalogo>): Promise<TipoInsumoCatalogo> {
    const res = await apiClient.post<TipoInsumoCatalogo>('/tipos-insumo', data);
    return res.data;
  },
  async updateTipoInsumo(id: number, data: Partial<TipoInsumoCatalogo>): Promise<TipoInsumoCatalogo> {
    const res = await apiClient.put<TipoInsumoCatalogo>(`/tipos-insumo/${id}`, data);
    return res.data;
  },
  async deleteTipoInsumo(id: number): Promise<void> {
    await apiClient.delete(`/tipos-insumo/${id}`);
  },

  // Laboratorios de Referencia
  async getLaboratoriosReferencia(activoOnly = false): Promise<LaboratorioReferencia[]> {
    const res = await apiClient.get<LaboratorioReferencia[]>('/laboratorios-referencia', { params: { activo_only: activoOnly } });
    return res.data;
  },
  async createLaboratorioReferencia(data: Partial<LaboratorioReferencia>): Promise<LaboratorioReferencia> {
    const res = await apiClient.post<LaboratorioReferencia>('/laboratorios-referencia', data);
    return res.data;
  },
  async updateLaboratorioReferencia(id: number, data: Partial<LaboratorioReferencia>): Promise<LaboratorioReferencia> {
    const res = await apiClient.put<LaboratorioReferencia>(`/laboratorios-referencia/${id}`, data);
    return res.data;
  },
  async deleteLaboratorioReferencia(id: number): Promise<void> {
    await apiClient.delete(`/laboratorios-referencia/${id}`);
  }
};
