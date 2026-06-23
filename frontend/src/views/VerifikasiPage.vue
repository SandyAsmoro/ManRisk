<!-- ...\ManRiskMSKI\frontend\src\views\VerifikasiPage.vue -->

<template>
  <div class="p-6 mx-auto max-w-7xl">

    <div class="flex flex-col items-start justify-between gap-4 mb-6 sm:flex-row sm:items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">Antrean Verifikasi Data</h2>
        <p class="mt-1 text-sm text-gray-500">Tinjau dan setujui laporan risiko yang dikirim oleh masing-masing seksi.</p>
      </div>
      <button @click="fetchPendingAssessments" class="px-4 py-2 text-sm font-semibold text-blue-600 transition border border-blue-200 rounded hover:bg-blue-50">
        Refresh Data
      </button>
    </div>

    <div class="space-y-4">
      <div v-if="pendingAssessments.length === 0" class="p-12 text-center bg-white border border-gray-100 shadow-sm rounded-xl">
        <span class="text-4xl">🎉</span>
        <h3 class="mt-4 text-lg font-bold text-gray-800">Antrean Kosong</h3>
        <p class="text-gray-500">Semua data risiko yang dikirim seksi telah ditinjau.</p>
      </div>

      <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div v-for="item in pendingAssessments" :key="item.id" class="flex flex-col p-5 bg-white border border-gray-200 shadow-sm rounded-xl">
          <div class="flex items-center justify-between mb-3">
            <span class="px-2.5 py-1 text-xs font-bold text-blue-800 bg-blue-100 rounded">{{ item.section }}</span>
            <span class="text-xs font-semibold text-gray-500">{{ item.quarter }} {{ item.year }}</span>
          </div>

          <h4 class="mb-1 text-sm font-bold text-gray-800">{{ item.indicator_code }}</h4>
          <p class="mb-4 text-xs text-gray-600 line-clamp-2">{{ item.indicator_name }}</p>

          <div class="flex items-center gap-2 mb-4">
            <span class="text-xs text-gray-500">Skor Risiko:</span>
            <span :class="getCategoryBg(item.risk_category)" class="px-2 py-1 text-xs font-bold text-white rounded">{{ item.risk_value }} - {{ item.risk_category }}</span>
          </div>

          <div v-if="item.has_document" class="flex items-center justify-between p-2 mb-4 border border-blue-100 rounded-lg bg-blue-50">
            <span class="text-xs text-blue-800 truncate max-w-[140px]" :title="item.document_name">
              📎 {{ item.document_name }}
            </span>
            <button @click="downloadDocument(item.id, item.document_name)" class="text-xs font-bold text-blue-700 transition hover:text-blue-900 hover:underline">
              Unduh Bukti
            </button>
          </div>
          <div v-else class="p-2 mb-4 border border-gray-100 rounded-lg bg-gray-50">
            <span class="text-xs italic text-gray-400">Tidak ada lampiran dokumen</span>
          </div>

          <div class="flex gap-2 mt-auto">
            <button @click="verifyAssessment(item.id, 'approve')" class="flex-1 py-1.5 text-xs font-bold text-white bg-green-600 rounded hover:bg-green-700 transition">Setujui</button>
            <button @click="verifyAssessment(item.id, 'reject')" class="flex-1 py-1.5 text-xs font-bold text-white bg-red-600 rounded hover:bg-red-700 transition">Tolak (Revisi)</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api';

const pendingAssessments = ref([]);

const fetchPendingAssessments = async () => {
  try {
    const res = await api.get('/admin/assessments/pending');
    pendingAssessments.value = res.data.data || [];
  } catch (error) {
    console.error("Gagal mengambil data antrean:", error);
  }
};

const verifyAssessment = async (id, action) => {
  const actionText = action === 'approve' ? 'menyetujui' : 'menolak dan mengembalikan';
  if (confirm(`Apakah Anda yakin ingin ${actionText} data ini?`)) {
    try {
      const res = await api.post(`/admin/assessments/${id}/verify`, { action });
      alert(res.data.message);
      fetchPendingAssessments(); // Segarkan antrean setelah berhasil
    } catch (error) {
      alert(error.response?.data?.message || "Gagal memproses verifikasi.");
    }
  }
};

const getCategoryBg = (cat) => {
  if (cat === 'Biru' || cat === 'Risiko Rendah') return 'bg-blue-500';
  if (cat === 'Hijau' || cat === 'Risiko Sedang Rendah') return 'bg-green-500';
  if (cat === 'Kuning' || cat === 'Risiko Sedang') return 'bg-yellow-400 text-yellow-900';
  if (cat === 'Jingga' || cat === 'Risiko Tinggi') return 'bg-orange-500';
  if (cat === 'Merah' || cat === 'Risiko Sangat Tinggi') return 'bg-red-600';
  return 'bg-gray-500';
};

// Download Dokumen Bukti
const downloadDocument = async (assessmentId, filename) => {
  try {
    const res = await api.get(`/risiko/assessments/${assessmentId}/document`, { responseType: 'blob' });

    const url = window.URL.createObjectURL(new Blob([res.data], { type: res.headers['content-type'] }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();

    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error(error);
    alert("Gagal mengunduh dokumen bukti pendukung. Dokumen mungkin telah dihapus atau rusak.");
  }
};

onMounted(() => {
  fetchPendingAssessments();
});
</script>