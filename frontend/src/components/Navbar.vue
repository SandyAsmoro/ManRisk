<!-- ...\ManRiskMSKI\frontend\src\components\Navbar.vue -->

<template>
  <header class="flex items-center justify-between px-6 py-3 bg-white shadow-sm shrink-0">

    <h1 class="text-base font-semibold text-gray-700">
      {{ pageTitle }}
    </h1>

    <div class="flex items-center gap-4">

      <span
        v-if="authStore.user?.section"
        class="hidden sm:inline-block text-xs bg-blue-100 text-blue-700 font-medium px-2.5 py-1 rounded-full"
      >
        {{ authStore.user.section }}
      </span>

      <span class="hidden text-sm font-medium text-gray-600 sm:block">
        {{ authStore.user?.full_name || authStore.user?.username || 'Pengguna' }}
      </span>

      <button
        @click="handleLogout"
        :disabled="isLoggingOut"
        class="flex items-center gap-1.5 text-sm text-red-500 hover:text-red-700 disabled:opacity-50 transition font-medium"
        title="Keluar"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v1"/>
        </svg>
        <span class="hidden sm:inline">{{ isLoggingOut ? 'Keluar...' : 'Logout' }}</span>
      </button>

    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/store/auth';

const router    = useRouter();
const route     = useRoute();
const authStore = useAuthStore();

const isLoggingOut = ref(false);

// 🚨 [PERBAIKAN T25]: Judul halaman otomatis berdasarkan nama rute indeks yang aktif
const pageTitle = computed(() => {
  const titleMap = {
    'Dashboard': 'Dashboard Utama',
    'InputData': 'Input Penilaian Risiko',
    'Laporan': 'Laporan & Rekapitulasi Kerja',
    'AnalisisPerubahan': 'Analisis Perubahan & Tren Risiko', // Sinkronisasi Judul Halaman Baru
    'ChangePassword': 'Wajib Memperbarui Kata Sandi',
    'AdminPage': 'Kelola User & Akun Pegawai',
    'AdminVerifikasi': 'Antrean Verifikasi Data Risiko',
    'Register': 'Registrasi Akun Pegawai Baru',
    'AdminIndicators': 'Panel Pengelolaan Indikator & Target'
  };
  return titleMap[route.name] || 'Sistem Manajemen Risiko KPPN';
});

const handleLogout = async () => {
  if (confirm('Apakah Anda yakin ingin keluar dari aplikasi?')) {
    isLoggingOut.value = true;
    try {
      await authStore.logout();
      router.push('/login');
    } catch (error) {
      console.error('Gagal memproses pemutusan sesi login:', error);
    } finally {
      isLoggingOut.value = false;
    }
  }
};
</script>