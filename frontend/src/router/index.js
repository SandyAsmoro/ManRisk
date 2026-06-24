// ...\ManRiskMSKI\frontend\src\router\index.js

import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/store/auth';

import LoginPage from '@/views/LoginPage.vue';
import DashboardPage from '@/views/DashboardPage.vue';
import InputDataPage from '@/views/InputDataPage.vue';
import LaporanPage from '@/views/LaporanPage.vue';
import RegisterPage from '@/views/RegisterPage.vue';
import AdminPage from '@/views/AdminPage.vue';
import VerifikasiPage from '@/views/VerifikasiPage.vue';
import ChangePasswordPage from '@/views/ChangePasswordPage.vue';
import AnalisisPerubahan from '@/views/AnalisisPerubahan.vue';
import RiwayatDataPage from '@/views/RiwayatDataPage.vue';
import AuditLogPage from '@/views/AuditLogPage.vue';
import UbahPasswordPage from '@/views/UbahPasswordPage.vue';

const routes = [
  { 
    path: '/login', 
    name: 'Login', 
    component: LoginPage 
  },
  { 
    path: '/', 
    name: 'Dashboard', 
    component: DashboardPage,
    meta: { requiresAuth: true }
  },
  { 
    path: '/input', 
    name: 'InputData', 
    component: InputDataPage, 
    meta: { requiresAuth: true }
  },
  { 
    path: '/riwayat', 
    name: 'RiwayatData', 
    component: RiwayatDataPage, 
    meta: { requiresAuth: true } // 🚨 Rute Riwayat & Revisi Data
  },
  { 
    path: '/laporan', 
    name: 'Laporan', 
    component: LaporanPage, 
    meta: { requiresAuth: true }
  },
  { 
    path: '/analisis-perubahan', 
    name: 'AnalisisPerubahan', 
    component: AnalisisPerubahan, 
    meta: { requiresAuth: true }
  },
  { 
    path: '/change-password', 
    name: 'ChangePassword', 
    component: ChangePasswordPage, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/admin/verifikasi', 
    name: 'AdminVerifikasi', 
    component: VerifikasiPage, 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  { 
    path: '/admin', 
    name: 'AdminPage', 
    component: AdminPage, 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  { 
    path: '/register', 
    name: 'Register', 
    component: RegisterPage, 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  { 
    path: '/audit-log', 
    name: 'AuditLog', 
    component: AuditLogPage, 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  {
    path: '/admin/indicators',
    name: 'AdminIndicators', // Harus sama dengan key di titleMap Navbar.vue
    component: () => import('@/views/AdminIndicator.vue'), // Sesuaikan lokasi filenya
    meta: { requiresAuth: true, role: 'admin' } // Jika Anda memakai navigation guard untuk admin
  },
  { 
    path: '/ubah-password', 
    name: 'UbahPassword', 
    component: UbahPasswordPage, 
    meta: { requiresAuth: true, requiresAdmin: true } // 👈 Kunci keamanan ada di sini
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;
  const userRole = authStore.user?.role;
  const mustChangePassword = authStore.user?.must_change_password;

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login');
  } 
  
  if (isAuthenticated && mustChangePassword && to.name !== 'ChangePassword') {
    return next({ name: 'ChangePassword' });
  }

  if (to.meta.requiresAdmin && userRole !== 'admin') {
    alert("Akses Ditolak: Halaman ini hanya diperuntukkan bagi Administrator.");
    return next('/');
  }

  next();
});

export default router;