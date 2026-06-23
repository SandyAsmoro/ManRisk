<!-- ...\ManRiskMSKI\frontend\src\components\Sidebar.vue -->

<template>
  <aside class="flex flex-col w-64 text-white bg-primary">
    <div class="p-4 text-center border-b border-secondary">
      <h2 class="text-xl font-bold">ManRisk KPPN</h2>
    </div>
    <nav class="flex-1 p-4 space-y-2">
      <router-link to="/" class="block p-3 transition rounded hover:bg-secondary" active-class="bg-secondary">
        Dashboard
      </router-link>
      <router-link to="/input" class="block p-3 transition rounded hover:bg-secondary" active-class="bg-secondary">
        Input Data Risiko
      </router-link>
      
      <router-link to="/riwayat" class="block p-3 transition rounded hover:bg-secondary" active-class="bg-secondary">
        Riwayat & Edit Data
      </router-link>
      
      <router-link to="/laporan" class="block p-3 transition rounded hover:bg-secondary" active-class="bg-secondary">
        Laporan & Rekap
      </router-link>
      
      <router-link to="/analisis-perubahan" class="block p-3 transition rounded hover:bg-secondary" active-class="bg-secondary">
        Analisis Perubahan
      </router-link>
      
      <hr class="my-4 border-secondary" />

      <router-link v-if="authStore.user?.role === 'admin'" to="/admin/indicators" class="block p-3 transition rounded hover:bg-secondary" active-class="bg-secondary">
        Kelola Indikator & Target
      </router-link>

      <router-link v-if="authStore.user?.role === 'admin'" to="/admin/verifikasi" class="block p-3 transition rounded hover:bg-secondary" active-class="bg-secondary">
        Antrean Verifikasi Data
      </router-link>

      <router-link v-if="authStore.user?.role === 'admin'" to="/admin" class="block p-3 transition rounded hover:bg-secondary" active-class="bg-secondary">
        Kelola User
      </router-link>

      <router-link v-if="authStore.user?.role === 'admin'" to="/audit-log" class="block p-3 transition rounded hover:bg-secondary" active-class="bg-secondary">
        Log Aktivitas (Audit)
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { useAuthStore } from '@/store/auth';
const authStore = useAuthStore();
</script>