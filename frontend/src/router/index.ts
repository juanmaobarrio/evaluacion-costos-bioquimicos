import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guestOnly: true }
    },
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
        },
        {
          path: 'determinaciones',
          name: 'determinaciones',
          component: () => import('@/views/DeterminacionesView.vue'),
        },
        {
          path: 'insumos',
          name: 'insumos',
          component: () => import('@/views/InsumosView.vue'),
        },
        {
          path: 'equipos',
          name: 'equipos',
          component: () => import('@/views/EquiposView.vue'),
        },
        {
          path: 'protocolos',
          name: 'protocolos',
          component: () => import('@/views/ProtocolosView.vue'),
        },
        {
          path: 'gastos-fijos',
          name: 'gastos-fijos',
          component: () => import('@/views/GastosFijosView.vue'),
        },
        {
          path: 'simulador',
          name: 'simulador',
          component: () => import('@/views/SimuladorView.vue'),
        },
        {
          path: 'conciliacion',
          name: 'conciliacion',
          component: () => import('@/views/ConciliacionView.vue'),
        },
        {
          path: 'configuracion',
          name: 'configuracion',
          component: () => import('@/views/ConfiguracionView.vue'),
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  if (to.meta.requiresAuth && !token) {
    next('/login');
  } else if (to.meta.guestOnly && token) {
    next('/');
  } else {
    next();
  }
});

export default router;
