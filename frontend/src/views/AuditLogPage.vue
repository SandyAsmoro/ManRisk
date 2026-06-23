<!-- ...\ManRiskMSKI\frontend\src\views\AuditLogPage.vue -->

<template>
  <div class="p-6 mx-auto space-y-6 max-w-7xl">
    <div class="flex items-center justify-between p-6 bg-white border border-gray-100 shadow-sm rounded-xl">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">Audit Trail & Log Aktivitas</h2>
        <p class="mt-1 text-sm text-gray-500">Pemantauan rekam jejak aktivitas kritis pengguna di dalam sistem.</p>
      </div>
      <button @click="fetchLogs" class="px-4 py-2 font-bold text-blue-600 transition border border-blue-200 rounded-lg bg-blue-50 hover:bg-blue-100">
        🔄 Segarkan Data
      </button>
    </div>

    <div class="overflow-hidden bg-white border border-gray-100 shadow-sm rounded-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left border-collapse">
          <thead class="text-white bg-gray-900 border-b">
            <tr>
              <th class="p-4 text-xs font-bold tracking-wider uppercase">Waktu (UTC)</th>
              <th class="p-4 text-xs font-bold tracking-wider uppercase">Pengguna</th>
              <th class="p-4 text-xs font-bold tracking-wider text-center uppercase">Aksi / Event</th>
              <th class="p-4 text-xs font-bold tracking-wider uppercase">Modul Target</th>
              <th class="p-4 text-xs font-bold tracking-wider uppercase">Keterangan Detail</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="log in logs" :key="log.id" class="transition-colors hover:bg-gray-50">
              <td class="p-4 font-mono text-xs text-gray-500 whitespace-nowrap">{{ formatDate(log.timestamp) }}</td>
              <td class="p-4 font-bold text-gray-800">👤 {{ log.username }}</td>
              <td class="p-4 text-center">
                <span class="px-2 py-1 text-[10px] font-bold uppercase rounded border" :class="getActionBadge(log.action)">
                  {{ log.action }}
                </span>
              </td>
              <td class="p-4 font-medium text-gray-600">{{ log.resource_type || '-' }}</td>
              <td class="p-4 text-gray-600">{{ log.details || '-' }}</td>
            </tr>
            <tr v-if="logs.length === 0">
              <td colspan="5" class="p-12 font-medium text-center text-gray-400">Belum ada catatan aktivitas yang terekam.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api';

const logs = ref([]);

const fetchLogs = async () => {
  try {
    const res = await api.get('/audit');
    logs.value = res.data.data;
  } catch (error) {
    console.error("Gagal menarik data audit:", error);
  }
};

const formatDate = (isoString) => {
  if (!isoString) return '-';
  const d = new Date(isoString);
  return d.toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' });
};

const getActionBadge = (action) => {
  if (action.includes('APPROVE')) return 'bg-green-50 text-green-700 border-green-200';
  if (action.includes('REJECT') || action.includes('DELETE')) return 'bg-red-50 text-red-700 border-red-200';
  if (action.includes('LOGIN')) return 'bg-blue-50 text-blue-700 border-blue-200';
  return 'bg-gray-50 text-gray-700 border-gray-200';
};

onMounted(() => {
  fetchLogs();
});
</script>