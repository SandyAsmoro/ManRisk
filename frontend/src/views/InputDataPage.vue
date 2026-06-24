<!-- ...\ManRiskMSKI\frontend\src\views\InputDataPage.vue -->

<template>
  <div class="max-w-3xl mx-auto space-y-6">
    
    <div v-if="isOffline" class="p-4 mb-2 transition-all border-l-4 border-red-500 rounded-r-lg shadow-sm bg-red-50">
      <div class="flex items-center">
        <svg class="w-6 h-6 mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        <p class="text-sm text-red-700">
          <strong>Koneksi terputus!</strong> Data yang Anda ketik aman dan tersimpan sementara di browser Anda (Local Storage).
        </p>
      </div>
    </div>

    <div class="p-6 bg-white border border-gray-100 rounded-lg shadow">
      <h2 class="mb-2 text-2xl font-bold text-gray-800">Input Data Risiko</h2>
      <p class="mb-6 text-sm text-gray-500">Isi formulir ini untuk setiap indikator. Data akan disimpan sebagai Draf hingga Anda melakukan Kirim Final.</p>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Indikator Risiko</label>
          <select v-model="form.indicator_id" @change="handleIndicatorChange" class="w-full p-2 mt-1 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500" required>
            <option value="" disabled>-- Pilih Indikator --</option>
            <option v-for="i in indicators" :key="i.id" :value="i.id">{{ i.code }} - {{ i.iru || i.name }}</option>
          </select>
          
          <div v-if="selectedIndicator && selectedIndicator.secondary_pics" class="flex items-center gap-2 mt-2">
            <span class="px-2 py-1 text-xs font-bold text-purple-700 bg-purple-100 border border-purple-200 rounded">🤝 Indikator Bersama</span>
            <span class="text-xs text-gray-600">Primary: <strong>{{ selectedIndicator.pic }}</strong> | Secondary: <strong>{{ selectedIndicator.secondary_pics }}</strong></span>
          </div>
        </div>

        <div v-if="isReadOnly" class="p-4 mb-4 border-l-4 border-yellow-400 bg-yellow-50">
          <p class="text-sm text-yellow-700">
            <strong>Mode Hanya Baca (Read-Only).</strong> Anda adalah PIC Pendamping untuk indikator ini. Pengisian data hanya dapat dilakukan oleh <strong>{{ selectedIndicator?.pic }}</strong>.
          </p>
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="block text-sm font-medium text-gray-700">Triwulan (Periode)</label>
            <select v-model="form.quarter" @change="checkAndLoadDraft" :disabled="isReadOnly" class="w-full p-2 mt-1 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100" required>
              <option value="Q1">Triwulan 1 (Jan - Mar)</option>
              <option value="Q2">Triwulan 2 (Apr - Jun)</option>
              <option value="Q3">Triwulan 3 (Jul - Sep)</option>
              <option value="Q4">Triwulan 4 (Okt - Des)</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Tindakan Mitigasi</label>
            <input type="text" v-model="form.mitigation_action" :disabled="isReadOnly" class="w-full p-2 mt-1 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100" placeholder="Langkah mitigasi..." />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Frekuensi (1-5)</label>
            <input type="number" v-model="form.frequency" min="1" max="5" :disabled="isReadOnly" class="w-full p-2 mt-1 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100" required />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Dampak (1-5)</label>
            <input type="number" v-model="form.impact" min="1" max="5" :disabled="isReadOnly" class="w-full p-2 mt-1 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100" required />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Bukti Pendukung (Opsional)</label>
          <input type="file" @change="handleFileChange" :disabled="isReadOnly" class="w-full p-2 mt-1 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100" accept=".pdf,.png,.jpg,.jpeg,.zip" />
          <p class="mt-1 text-xs text-gray-500">Format diizinkan: PDF, JPG, PNG, ZIP. Maksimal 5MB.</p>
        </div>

        <div v-if="alreadyFilledIds.includes(form.indicator_id)" class="p-4 mb-4 text-sm text-yellow-800 bg-yellow-100 border border-yellow-200 rounded-lg">
            ⚠️ <strong>Perhatian:</strong> Anda sudah mengisi indikator ini untuk {{ form.quarter }}. 
            Silakan ke menu <strong>"Riwayat & Edit Data"</strong> jika ingin mengubah nilainya.
        </div>

        <button type="submit" :disabled="isLoading || isReadOnly || isOffline" class="w-full p-2 font-semibold text-white transition bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
          {{ isLoading ? 'Menyimpan...' : (isReadOnly ? 'Form Terkunci' : (isOffline ? 'Menunggu Koneksi...' : 'Simpan Data (Draf)')) }}
        </button>
      </form>
    </div>

    <div class="flex flex-col items-center p-6 text-center border border-blue-200 rounded-lg shadow-sm bg-blue-50">
      <div class="mb-4">
        <svg class="w-12 h-12 mx-auto mb-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <h3 class="text-lg font-bold text-gray-800">Kirim Dokumen Final Triwulan</h3>
        <p class="max-w-lg mx-auto mt-1 text-sm text-gray-600">
          Pastikan Anda telah mengisi seluruh 25 indikator risiko untuk periode ini. 
          Data yang telah di-Submit tidak dapat diubah kembali.
        </p>
      </div>
      
      <div class="flex flex-wrap items-center justify-center w-full gap-3">
        <select v-model="batchQuarter" class="w-32 p-2 border border-gray-300 rounded shadow-sm focus:ring-blue-500 focus:border-blue-500">
          <option value="Q1">Triwulan 1</option>
          <option value="Q2">Triwulan 2</option>
          <option value="Q3">Triwulan 3</option>
          <option value="Q4">Triwulan 4</option>
        </select>
        
        <input type="number" v-model="batchYear" class="p-2 border border-gray-300 rounded shadow-sm w-28 focus:ring-blue-500 focus:border-blue-500" placeholder="Tahun" />
        
        <button @click="handleBatchSubmit" :disabled="isBatchLoading || isOffline" class="flex items-center gap-2 px-6 py-2 font-bold text-white transition bg-green-600 rounded shadow hover:bg-green-700 disabled:opacity-50">
          <span v-if="isBatchLoading">Memvalidasi...</span>
          <span v-else>Kirim Final (Batch Submit)</span>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue';
import { useRiskStore } from '@/store/risk';
import { useAuthStore } from '@/store/auth';
import api from '@/utils/api';

const store = useRiskStore();
const authStore = useAuthStore();
const isLoading = ref(false);
const isBatchLoading = ref(false);
const alreadyFilledIds = ref([]);

// 🚨 T24: State Deteksi Jaringan Offline
const isOffline = ref(!navigator.onLine);
const updateOnlineStatus = () => {
  isOffline.value = !navigator.onLine;
};

const form = ref({
  indicator_id: '', 
  quarter: 'Q1', 
  frequency: 1, 
  impact: 1, 
  mitigation_action: '',
  file: null 
});

const batchQuarter = ref('Q1');
const batchYear = ref(new Date().getFullYear());

const selectedIndicator = ref(null);
const isReadOnly = ref(false);

onMounted(() => {
  store.fetchIndicators();
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
});

onUnmounted(() => {
  window.removeEventListener('online', updateOnlineStatus);
  window.removeEventListener('offline', updateOnlineStatus);
});

const indicators = computed(() => store.indicators);

const checkAccess = () => {
  const currentIndicator = indicators.value.find(i => i.id === form.value.indicator_id);
  selectedIndicator.value = currentIndicator;
  
  if (currentIndicator) {
    const userSection = authStore.user?.section;
    if (userSection !== currentIndicator.pic && authStore.user?.role !== 'admin') {
      isReadOnly.value = true;
    } else {
      isReadOnly.value = false;
    }
  }
};

// 🚨 T24: Generate Kunci Local Storage Dinamis
const getDraftKey = () => {
  if (!form.value.indicator_id) return null;
  return `draft_assessment_${authStore.user?.section}_${form.value.quarter}_${batchYear.value}_${form.value.indicator_id}`;
};

// 🚨 T24: Watcher untuk Auto-Save ketikan pengguna secara Live
watch(
  [
    () => form.value.frequency,
    () => form.value.impact,
    () => form.value.mitigation_action
  ],
  () => {
    // Jalankan auto-save HANYA jika form tidak read-only dan indikator sudah dipilih
    if (isReadOnly.value || !form.value.indicator_id) return;
    
    const key = getDraftKey();
    if (key) {
      const draftData = {
        frequency: form.value.frequency,
        impact: form.value.impact,
        mitigation_action: form.value.mitigation_action
      };
      localStorage.setItem(key, JSON.stringify(draftData));
      console.log(`💾 [AUTO-SAVE]: Draf untuk kunci ${key} berhasil diperbarui.`);
    }
  }
);

// 🚨 T24: Fungsi mengecek dan menawarkan Draft Tersimpan
const checkAndLoadDraft = () => {
  if (isReadOnly.value || !form.value.indicator_id) return;

  const key = getDraftKey();
  if (key) {
    const saved = localStorage.getItem(key);
    if (saved) {
      if (confirm('Ada draft lokal yang belum tersimpan untuk indikator & triwulan ini. Lanjutkan pengisian draft?')) {
        const parsed = JSON.parse(saved);
        form.value.frequency = parsed.frequency || 1;
        form.value.impact = parsed.impact || 1;
        form.value.mitigation_action = parsed.mitigation_action || '';
      } else {
        localStorage.removeItem(key); // Hapus jika pengguna memilih "Cancel"
      }
    }
  }
};

const handleIndicatorChange = () => {
  checkAccess();
  checkAndLoadDraft(); // Panggil pengecekan draft saat indikator diganti
};

const handleFileChange = (e) => form.value.file = e.target.files[0];

const handleSubmit = async () => {
  isLoading.value = true;
  try {
    const payload = { ...form.value };
    delete payload.file;
    
    const res = await api.post('/risiko/assessment', payload);

    if (res.data.assessment_id && form.value.file) {
      const formData = new FormData();
      formData.append('file', form.value.file);
      formData.append('assessment_id', res.data.assessment_id);

      await api.post('/laporan/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    }
    
    alert("Data berhasil disimpan sebagai draf sementara!");
    
    // 🚨 T24: Hapus Draf dari Local Storage setelah sukses masuk ke database
    const key = getDraftKey();
    if (key) localStorage.removeItem(key);
    
    form.value = { 
      indicator_id: '', 
      quarter: form.value.quarter, 
      frequency: 1, 
      impact: 1, 
      mitigation_action: '',
      file: null 
    };
    batchQuarter.value = form.value.quarter;
    isReadOnly.value = false;
    selectedIndicator.value = null;
    
  } catch (error) {
    alert(error.response?.data?.message || "Terjadi kesalahan saat menyimpan data.");
  } finally {
    isLoading.value = false;
  }
};

const checkAlreadyFilled = async () => {
  try {
    // Tarik data riwayat di triwulan dan tahun yang dipilih
    const params = { quarter: form.value.quarter, year: new Date().getFullYear() };
    const res = await api.get('/risiko/assessments', { params });
    
    if (res.data && res.data.data) {
      // Simpan HANYA indicator_id nya saja ke dalam array
      alreadyFilledIds.value = res.data.data.map(item => item.indicator_id);
    }
  } catch (error) {
    console.error("Gagal mengecek duplikasi:", error);
  }
};

// Panggil fungsi ini setiap kali User mengganti pilihan Triwulan di Form
watch(() => form.value.quarter, () => {
  checkAlreadyFilled();
});

onMounted(() => {
  checkAlreadyFilled(); // Panggil juga saat halaman pertama dimuat
});

const handleBatchSubmit = async () => {
  const confirmMsg = `Apakah Anda yakin ingin mengirim dokumen final untuk ${batchQuarter.value} tahun ${batchYear.value}?\n\nPERINGATAN: Seluruh 25 data indikator yang telah dikirim akan dikunci secara permanen dan tidak bisa diedit lagi.`;
  
  if (confirm(confirmMsg)) {
    isBatchLoading.value = true;
    try {
      const response = await api.post('/risiko/assessments/batch-submit', {
        quarter: batchQuarter.value,
        year: batchYear.value
      });
      alert(response.data.message);
    } catch (error) {
      if (error.response?.status === 400 && error.response.data.missing_indicators) {
        const missingList = error.response.data.missing_indicators.join('\n- ');
        alert(`GAGAL MENGIRIM!\n\nMohon lengkapi indikator berikut terlebih dahulu:\n- ${missingList}`);
      } else {
        alert(error.response?.data?.message || "Terjadi kesalahan sistem saat memproses batch submit.");
      }
    } finally {
      isBatchLoading.value = false;
    }
  }
};
</script>