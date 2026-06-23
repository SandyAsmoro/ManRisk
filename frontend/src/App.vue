<!-- ...\ManRiskMSKI\frontend\src\App.vue -->

<template>
  <div v-if="authStore.isAuthenticated" class="flex h-screen overflow-hidden bg-gray-100">
    <Sidebar />

    <div class="flex flex-col flex-1 w-full">
      <Navbar />
      
      <main class="h-full p-6 overflow-y-auto">
        <router-view></router-view>
      </main>
    </div>
  </div>

  <div v-else>
    <router-view></router-view>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/store/auth';
import Sidebar from '@/components/Sidebar.vue';
import Navbar from '@/components/Navbar.vue';

const authStore = useAuthStore();
</script>