import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient } from '@/services/api';
import type { User } from '@/types';

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'));
  const user = ref<User | null>(
    localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null
  );
  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === 'admin');
  const isBioquimico = computed(() => user.value?.role === 'admin' || user.value?.role === 'bioquimico');

  async function login(formData: FormData | URLSearchParams) {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      token.value = response.data.access_token;
      user.value = response.data.user;
      
      localStorage.setItem('token', token.value!);
      localStorage.setItem('user', JSON.stringify(user.value));
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error al iniciar sesión';
      return false;
    } finally {
      loading.value = false;
    }
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    isBioquimico,
    login,
    logout
  };
});
