<template>
  <div class="p-6 mx-auto space-y-8 max-w-7xl">
    
    <div class="p-6 bg-white border border-gray-100 shadow-sm rounded-xl">
      <h2 class="text-3xl font-bold tracking-tight text-gray-900">Pusat Laporan & Ekspor Data</h2>
      <p class="mt-1 text-sm text-gray-500">
        Unduh rekapitulasi data risiko yang <strong>telah disetujui (Verified)</strong> serta lampiran bukti pendukung untuk keperluan audit dan laporan Kanwil/Pusat.
      </p>
    </div>

    <div class="grid items-start grid-cols-1 gap-8 md:grid-cols-12">
      
      <div class="p-6 bg-white border border-gray-100 shadow-sm md:col-span-4 rounded-xl">
        <h3 class="pb-2 mb-4 text-lg font-bold text-gray-800 border-b">Filter Periode Laporan</h3>
        <div class="space-y-4">
          <div>
            <label class="block mb-1 text-sm font-semibold text-gray-700">Triwulan</label>
            <select v-model="filterQuarter" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Semua Triwulan</option>
              <option value="Q1">Q1 (Jan - Mar)</option>
              <option value="Q2">Q2 (Apr - Jun)</option>
              <option value="Q3">Q3 (Jul - Sep)</option>
              <option value="Q4">Q4 (Okt - Des)</option>
            </select>
          </div>
          <div>
            <label class="block mb-1 text-sm font-semibold text-gray-700">Tahun</label>
            <input type="number" v-model="filterYear" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 md:col-span-8 sm:grid-cols-2">
        
        <button @click="downloadExport('excel')" :disabled="isLoading" class="flex flex-col items-center justify-center p-6 transition border border-green-200 rounded-xl bg-green-50 hover:bg-green-100 disabled:opacity-50">
          <span class="mb-2 text-4xl">📊</span>
          <span class="font-bold text-green-800">Ekspor Excel (.xlsx)</span>
          <span class="mt-1 text-xs text-green-600">Data lengkap seluruh kolom</span>
        </button>

        <button @click="downloadExport('csv')" :disabled="isLoading" class="flex flex-col items-center justify-center p-6 transition border border-gray-200 rounded-xl bg-gray-50 hover:bg-gray-100 disabled:opacity-50">
          <span class="mb-2 text-4xl">📝</span>
          <span class="font-bold text-gray-800">Ekspor CSV (.csv)</span>
          <span class="mt-1 text-xs text-gray-500">Untuk diproses ke sistem lain</span>
        </button>

        <button @click="downloadExport('pdf')" :disabled="isLoading" class="flex flex-col items-center justify-center p-6 transition border border-red-200 rounded-xl bg-red-50 hover:bg-red-100 disabled:opacity-50">
          <span class="mb-2 text-4xl">📄</span>
          <span class="font-bold text-red-800">Cetak PDF (.pdf)</span>
          <span class="mt-1 text-xs text-red-600">Format laporan cetak A4</span>
        </button>

        <button @click="downloadExport('zip')" :disabled="isLoading" class="flex flex-col items-center justify-center p-6 transition border border-blue-200 rounded-xl bg-blue-50 hover:bg-blue-100 disabled:opacity-50">
          <span class="mb-2 text-4xl">🗂️</span>
          <span class="font-bold text-blue-800">Unduh Bukti (ZIP)</span>
          <span class="mt-1 text-xs text-center text-blue-600">Mengunduh semua file PDF/Foto dalam folder per seksi</span>
        </button>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/utils/api';

const filterQuarter = ref('');
const filterYear = ref(new Date().getFullYear());
const isLoading = ref(false);

const downloadExport = async (type) => {
  isLoading.value = true;
  try {
    const params = { quarter: filterQuarter.value, year: filterYear.value };
    
    // Tentukan URL berdasarkan tipe
    let urlEndpoint = type === 'zip' ? '/laporan/export-zip' : `/laporan/export?type=${type}`;
    
    // WAJIB: Response Type Blob agar file binary (Excel/PDF/ZIP) tidak rusak
    const response = await api.get(urlEndpoint, { params, responseType: 'blob' });
    
    // Cek apakah backend mengembalikan JSON Error (misal: Data Kosong)
    if (response.data.type === 'application/json') {
      const textData = await response.data.text();
      const json = JSON.parse(textData);
      alert(json.message || "Terjadi kesalahan.");
      return;
    }

    // Ekstrak tipe ekstensi untuk nama file
    let ext = type;
    if (type === 'excel') ext = 'xlsx';
    
    // Trigger download di browser
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Laporan_KPPN_${filterQuarter.value || 'All'}_${filterYear.value}.${ext}`);
    document.body.appendChild(link);
    link.click();
    
    // Bersihkan memory browser
    link.remove();
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    // Tangani error pembacaan JSON di dalam Blob Error
    if (error.response && error.response.data instanceof Blob) {
      try {
        const textData = await error.response.data.text();
        const json = JSON.parse(textData);
        alert(json.message);
      } catch (e) {
        alert("Gagal mengekspor file. Terjadi kesalahan jaringan atau server.");
      }
    } else {
      alert("Terjadi kesalahan jaringan.");
    }
  } finally {
    isLoading.value = false;
  }
};
</script>