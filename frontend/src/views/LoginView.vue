<template>
  <div class="min-h-screen bg-slate-950 flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
      <!-- Glow background decoration -->
      <div class="absolute -top-24 -right-24 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-24 -left-24 w-48 h-48 bg-teal-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <!-- Header -->
      <div class="text-center mb-8 relative z-10">
        <div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-950 mb-4">
          <i class="pi pi-chart-line text-white text-3xl"></i>
        </div>
        <h1 class="text-2xl font-extrabold text-white tracking-tight">BioCostos</h1>
        <p class="text-sm text-slate-400 mt-1">Gestión y Cálculo de Costos de Laboratorio</p>
      </div>

      <!-- Error message -->
      <div v-if="authStore.error" class="mb-5 p-3.5 bg-rose-950/50 border border-rose-800/80 rounded-xl flex items-center gap-3 text-rose-300 text-sm">
        <i class="pi pi-exclamation-circle text-lg"></i>
        <span>{{ authStore.error }}</span>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" class="space-y-4 relative z-10">
        <div>
          <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Correo Electrónico</label>
            <div class="relative">
              <i class="pi pi-envelope absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-sm"></i>
              <input v-model="email" type="email" required placeholder="admin@laboratorio.com" class="form-input !pl-11" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Contraseña</label>
            <div class="relative">
              <i class="pi pi-lock absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-sm"></i>
              <input v-model="password" type="password" required placeholder="••••••••" class="form-input !pl-11" />
            </div>
        </div>

        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full btn-primary py-3 text-base mt-2"
        >
          <i v-if="authStore.loading" class="pi pi-spin pi-spinner"></i>
          <span>{{ authStore.loading ? 'Verificando...' : 'Iniciar Sesión' }}</span>
        </button>
      </form>

      <!-- Quick Demo Login Buttons -->
      <div class="mt-8 pt-6 border-t border-slate-800 text-center relative z-10">
        <p class="text-xs text-slate-400 mb-3">Acceso rápido con datos semilla:</p>
        <div class="flex gap-2 justify-center">
          <button
            @click="fillCredentials('admin@laboratorio.com', 'admin123')"
            type="button"
            class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-medium text-emerald-400 transition-colors"
          >
            Admin (Full)
          </button>
          <button
            @click="fillCredentials('bioquimico@laboratorio.com', 'bio123')"
            type="button"
            class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-medium text-teal-400 transition-colors"
          >
            Bioquímico Jefe
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('admin@laboratorio.com');
const password = ref('admin123');

const fillCredentials = (u: string, p: string) => {
  email.value = u;
  password.value = p;
};

const handleLogin = async () => {
  const formData = new URLSearchParams();
  formData.append('username', email.value);
  formData.append('password', password.value);

  const success = await authStore.login(formData);
  if (success) {
    router.push('/');
  }
};
</script>
