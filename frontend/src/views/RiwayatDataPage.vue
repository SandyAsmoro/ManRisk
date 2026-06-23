<!-- ...\ManRiskMSKI\frontend\src\views\RiwayatDataPage.vue -->

<template>
  <div class="p-6 mx-auto space-y-6 max-w-7xl">
    
    <div class="flex flex-col items-start justify-between gap-4 p-6 bg-white border border-gray-100 shadow-sm rounded-xl md:flex-row md:items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">Riwayat & Revisi Data</h2>
        <p class="mt-1 text-sm text-gray-500">Kelola, lihat, dan revisi profil risiko yang pernah Anda kirimkan.</p>
      </div>
      
      <div class="flex items-center w-full gap-3 md:w-auto">
        <select v-model="filterQuarter" @change="fetchAssessments" class="w-full p-2 text-sm border border-gray-300 rounded-lg outline-none focus:ring-blue-500 md:w-32">
          <option value="">Semua Triwulan</option>
          <option value="Q1">Triwulan 1 (Q1)</option>
          <option value="Q2">Triwulan 2 (Q2)</option>
          <option value="Q3">Triwulan 3 (Q3)</option>
          <option value="Q4">Triwulan 4 (Q4)</option>
        </select>
        <input type="number" v-model="filterYear" @change="fetchAssessments" class="w-full p-2 text-sm border border-gray-300 rounded-lg outline-none focus:ring-blue-500 md:w-24" placeholder="Tahun" />
      </div>
    </div>

    <div class="overflow-hidden bg-white border border-gray-100 shadow-sm rounded-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left border-collapse">
          <thead class="text-gray-600 border-b bg-gray-50">
            <tr>
              <th class="p-4 font-semibold whitespace-nowrap">Indikator Risiko</th>
              <th class="p-4 font-semibold text-center">Periode</th>
              <th class="p-4 font-semibold text-center">Frek | Dampak</th>
              <th class="p-4 font-semibold">Tindakan Mitigasi</th>
              <th class="p-4 font-semibold text-center">Status</th>
              <th class="p-4 font-semibold text-center">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-if="isLoading">
              <td colspan="6" class="p-8 text-center text-gray-400">Memuat data riwayat...</td>
            </tr>
            <tr v-else-if="assessments.length === 0">
              <td colspan="6" class="p-8 text-center text-gray-400">Belum ada riwayat asesmen yang ditemukan.</td>
            </tr>
            <tr v-else v-for="item in assessments" :key="item.id" class="transition hover:bg-gray-50">
              
              <td class="p-4">
                <p class="font-bold text-gray-800">{{ item.indicator_code }}</p>
                <p class="text-xs text-gray-500 truncate max-w-[250px]">{{ item.indicator_name }}</p>
              </td>
              
              <td class="p-4 text-center">
                <span class="px-2 py-1 text-xs font-bold text-gray-700 bg-gray-200 rounded-md">{{ item.quarter }} {{ item.year }}</span>
              </td>
              
              <td class="p-4 text-center">
                <div class="inline-flex items-center justify-center gap-2">
                  <span class="px-2 py-1 text-xs font-bold text-gray-600 bg-white border border-gray-200 rounded">{{ item.frequency }}</span>
                  <span class="text-gray-400">×</span>
                  <span class="px-2 py-1 text-xs font-bold text-gray-600 bg-white border border-gray-200 rounded">{{ item.impact }}</span>
                </div>
              </td>
              
              <td class="p-4 text-gray-700">
                <p class="text-xs truncate max-w-[200px]" :title="item.mitigation_action">
                  {{ item.mitigation_action || 'Tidak ada mitigasi' }}
                </p>
              </td>
              
              <td class="p-4 text-center">
                <span :class="getStatusClass(item.status)" class="px-2.5 py-1 text-xs font-bold rounded-full border">
                  {{ formatStatus(item.status) }}
                </span>
              </td>
              
              <td class="p-4 text-center">
                <button 
                  v-if="item.status !== 'verified' && isQuarterEditable(item.quarter)"
                  @click="openEditModal(item)" 
                  class="px-3 py-1.5 text-xs font-bold text-blue-600 transition bg-blue-50 border border-blue-200 rounded hover:bg-blue-100 hover:text-blue-800"
                >
                  ✎ Edit
                </button>
                <span v-else class="text-xs italic text-gray-400">Terkunci</span>
              </td>

            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
      <div class="w-full max-w-lg p-6 overflow-hidden bg-white shadow-2xl rounded-2xl">
        <h3 class="mb-1 text-xl font-bold text-gray-800">Revisi Data Risiko</h3>
        <p class="mb-6 text-sm text-gray-500">{{ editForm.indicator_code }} - {{ editForm.indicator_name }}</p>
        
        <form @submit.prevent="saveEdit" class="space-y-5">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block mb-1 text-sm font-semibold text-gray-700">Tingkat Frekuensi (1-5)</label>
              <input type="number" min="1" max="5" v-model="editForm.frequency" class="w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500" required />
            </div>
            <div>
              <label class="block mb-1 text-sm font-semibold text-gray-700">Tingkat Dampak (1-5)</label>
              <input type="number" min="1" max="5" v-model="editForm.impact" class="w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500" required />
            </div>
          </div>
          
          <div>
            <label class="block mb-1 text-sm font-semibold text-gray-700">Tindakan Mitigasi</label>
            <textarea v-model="editForm.mitigation_action" rows="3" class="w-full px-4 py-2 text-sm border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500" placeholder="Jelaskan tindakan pencegahan..." required></textarea>
          </div>

          <div class="p-4 border border-gray-200 rounded-lg bg-gray-50">
            <label class="block mb-2 text-sm font-semibold text-gray-700">Bukti Pendukung</label>
            
            <div v-if="editForm.has_document" class="flex items-center justify-between p-2 mb-3 border border-blue-100 rounded-lg bg-blue-50">
              <span class="text-xs text-blue-800 truncate" :title="editForm.document_name">📎 {{ editForm.document_name }}</span>
              <button type="button" @click="deleteDocument(editForm.id)" class="text-xs font-bold text-red-600 hover:text-red-800 hover:underline">
                Hapus
              </button>
            </div>

            <input type="file" @change="handleFileChange" accept=".pdf,.png,.jpg,.jpeg,.zip" class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 file:mr-4 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
            <p class="mt-1 text-xs text-gray-500">Pilih file baru untuk mengganti file lama, atau biarkan kosong.</p>
          </div>

          <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
            <button type="button" @click="showModal = false" class="px-4 py-2 text-sm font-semibold text-gray-600 transition bg-gray-100 rounded-lg hover:bg-gray-200">Batal</button>
            <button type="submit" :disabled="isSaving" class="px-4 py-2 text-sm font-semibold text-white transition bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {{ isSaving ? 'Menyimpan...' : 'Simpan Perubahan' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api';
import { isQuarterEditable } from '@/utils/helpers'; // PENTING: Import helper waktu

const assessments = ref([]);
const isLoading = ref(true);

const filterQuarter = ref('');
const filterYear = ref(new Date().getFullYear());

const showModal = ref(false);
const isSaving = ref(false);
const editForm = ref({ id: '', frequency: 1, impact: 1, mitigation_action: '', indicator_code: '', indicator_name: '', file: null, has_document: false, document_name: '' });

const fetchAssessments = async () => {
  isLoading.value = true;
  try {
    const params = { quarter: filterQuarter.value, year: filterYear.value };
    const response = await api.get('/risiko/assessments', { params });
    if (response.data && response.data.data) {
      assessments.value = response.data.data;
    }
  } catch (error) {
    console.error("Gagal menarik data riwayat:", error);
  } finally {
    isLoading.value = false;
  }
};

const openEditModal = (item) => {
  editForm.value = { 
    id: item.id, 
    frequency: item.frequency, 
    impact: item.impact, 
    mitigation_action: item.mitigation_action,
    indicator_code: item.indicator_code,
    indicator_name: item.indicator_name,
    file: null,
    has_document: item.has_document,
    document_name: item.document_name
  };
  showModal.value = true;
};

// 2. Fungsi untuk menangkap file dari input
const handleFileChange = (e) => {
  if (e.target.files.length > 0) {
    editForm.value.file = e.target.files[0];
  } else {
    editForm.value.file = null;
  }
};

// 3. Perbarui fungsi saveEdit
const saveEdit = async () => {
  isSaving.value = true;
  try {
    let res;
    
    // Jika user memilih file baru, gunakan FormData
    if (editForm.value.file) {
      const formData = new FormData();
      formData.append('frequency', editForm.value.frequency);
      formData.append('impact', editForm.value.impact);
      formData.append('mitigation_action', editForm.value.mitigation_action);
      formData.append('file', editForm.value.file);
      
      res = await api.put(`/risiko/assessments/${editForm.value.id}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    } 
    // Jika tidak ada file baru, tetap gunakan JSON agar lebih ringan
    else {
      const payload = {
        frequency: editForm.value.frequency,
        impact: editForm.value.impact,
        mitigation_action: editForm.value.mitigation_action
      };
      res = await api.put(`/risiko/assessments/${editForm.value.id}`, payload);
    }
    
    alert(res.data.message);
    showModal.value = false;
    fetchAssessments(); // Reload tabel setelah sukses
  } catch (error) {
    alert(error.response?.data?.message || "Terjadi kesalahan saat menyimpan revisi.");
  } finally {
    isSaving.value = false;
  }
};

// 3. FUNGSI BARU: Fungsi untuk menghapus dokumen via API
const deleteDocument = async (assessmentId) => {
  if (confirm("Apakah Anda yakin ingin menghapus dokumen ini secara permanen?")) {
    try {
      const res = await api.delete(`/risiko/assessments/${assessmentId}/document`);
      alert(res.data.message);
      
      // Hilangkan visual dari form secara instan
      editForm.value.has_document = false;
      editForm.value.document_name = '';
      
      // Reload tabel di background
      fetchAssessments(); 
    } catch (error) {
      alert(error.response?.data?.message || "Gagal menghapus dokumen.");
    }
  }
};

const formatStatus = (status) => {
  const map = {
    'draft': 'Draft / Revisi',
    'submitted': 'Terkirim',
    'verified': 'Disetujui',
    'reject': 'Ditolak Admin'
  };
  return map[status] || status;
};

const getStatusClass = (status) => {
  const map = {
    'draft': 'bg-gray-100 text-gray-700 border-gray-300',
    'submitted': 'bg-blue-50 text-blue-700 border-blue-200',
    'verified': 'bg-green-50 text-green-700 border-green-200',
    'reject': 'bg-red-50 text-red-700 border-red-200'
  };
  return map[status] || 'bg-gray-100';
};

onMounted(() => {
  fetchAssessments();
});
</script>