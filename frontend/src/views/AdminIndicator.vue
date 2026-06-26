<template>
  <div class="p-6 mx-auto space-y-8 max-w-7xl">

    <div
      class="flex flex-col justify-between gap-4 p-6 bg-white border border-gray-100 shadow-sm md:flex-row md:items-center rounded-xl">
      <div>
        <h2 class="text-2xl font-bold tracking-tight text-gray-900 md:text-3xl">Kelola Data Indikator (Admin)</h2>
        <p class="mt-1 text-sm text-gray-500">
          Manajemen (CRUD) master data indikator beserta penetapan nilai awal P26 & R26.
        </p>
      </div>
      <button @click="openModal()"
        class="px-4 py-2 text-sm font-semibold text-white transition bg-blue-600 rounded-lg shadow-sm outline-none whitespace-nowrap hover:bg-blue-700 focus:ring-2 focus:ring-blue-500">
        + Tambah Indikator Baru
      </button>
    </div>

    <div class="overflow-x-auto bg-white border border-gray-100 shadow-sm rounded-xl">
      <!-- Hapus whitespace-nowrap dari tag table -->
      <table class="w-full text-sm text-left text-gray-600">
        <thead class="border-b border-gray-200 bg-gray-50 whitespace-nowrap">
          <tr>
            <th class="px-4 py-4 font-semibold text-gray-900">Kode</th>
            <th class="px-4 py-4 font-semibold text-gray-900">Deskripsi IRU</th>
            <th class="px-4 py-4 font-semibold text-gray-900">Deskripsi Indikator</th>
            <th class="px-4 py-4 font-semibold text-gray-900">PIC Utama</th>
            <th class="px-4 py-4 font-semibold text-center text-gray-900">P26</th>
            <th class="px-4 py-4 font-semibold text-center text-gray-900">R26</th>
            <th class="px-4 py-4 font-semibold text-center text-gray-900">Status</th>
            <th class="px-4 py-4 font-semibold text-center text-gray-900">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in indicators" :key="item?.id"
            class="transition-colors border-b border-gray-100 hover:bg-gray-50">
            
            <!-- Tambahkan align-top agar teks rapi di atas saat ada kolom yang wrap -->
            <td class="px-4 py-4 font-medium text-gray-900 align-top whitespace-nowrap">{{ item?.indicator_code }}</td>
            
            <!-- Gunakan whitespace-normal dan min-width agar teks bisa turun (wrap) dengan proporsional -->
            <td class="px-4 py-4 align-top whitespace-normal min-w-[200px] leading-relaxed">
              {{ item?.iru_description || '-' }}
            </td>
            
            <td class="px-4 py-4 align-top whitespace-normal min-w-[250px] leading-relaxed">
              {{ item?.indicator_description || '-' }}
            </td>
            
            <td class="px-4 py-4 align-top whitespace-nowrap">{{ item?.pic_section || '-' }}</td>
            <td class="px-4 py-4 font-mono font-medium text-center text-blue-600 align-top">{{ item?.p26_initial || '-' }}</td>
            <td class="px-4 py-4 font-mono font-medium text-center text-purple-600 align-top">{{ item?.r26_initial || '-' }}</td>
            
            <td class="px-4 py-4 text-center align-top whitespace-nowrap">
              <span v-if="item?.is_active"
                class="px-2 py-1 text-xs font-semibold text-green-700 bg-green-100 rounded-full">Aktif</span>
              <span v-else class="px-2 py-1 text-xs font-semibold text-red-700 bg-red-100 rounded-full">Nonaktif</span>
            </td>
            
            <td class="px-4 py-4 space-x-3 text-center align-top whitespace-nowrap">
              <button @click="openModal(item)"
                class="font-medium text-blue-600 transition hover:text-blue-800">Edit</button>
              <button @click="deleteIndicator(item?.id)"
                class="font-medium text-red-600 transition hover:text-red-800">Hapus</button>
            </td>
          </tr>

          <tr v-if="indicators.length === 0">
            <td colspan="8" class="px-4 py-12 font-medium text-center text-gray-400">
              Belum ada data indikator yang tersimpan.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto bg-gray-900 bg-opacity-50 backdrop-blur-sm">
      <div class="w-full max-w-3xl my-8 bg-white shadow-2xl rounded-xl">
        <div
          class="sticky top-0 z-10 flex items-center justify-between p-6 bg-white border-b border-gray-100 rounded-t-xl">
          <h3 class="text-xl font-bold text-gray-900">{{ form.id ? 'Edit Data Indikator' : 'Tambah Indikator Baru' }}
          </h3>
          <button @click="closeModal" class="text-2xl leading-none text-gray-400 hover:text-gray-600">&times;</button>
        </div>

        <form id="indicatorForm" @submit.prevent="saveData" class="p-6 space-y-5 overflow-y-auto max-h-[65vh]">

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="block mb-1 text-sm font-semibold text-gray-700">Kode Indikator <span
                  class="text-red-500">*</span></label>
              <input v-model="form.indicator_code" type="text" maxlength="20"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Cth: IKU-01" required />
            </div>
            <div>
              <label class="block mb-1 text-sm font-semibold text-gray-700">Tipe Indikator</label>
              <input v-model="form.indicator_type" type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Cth: KRI, KCI, KPI" />
            </div>
          </div>

          <div>
            <label class="block mb-1 text-sm font-semibold text-gray-700">Nama Indikator <span
                class="text-red-500">*</span></label>
            <input v-model="form.indicator_name" type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
              required />
          </div>

          <div>
            <label class="block mb-1 text-sm font-semibold text-gray-700">Deskripsi Indikator</label>
            <textarea v-model="form.indicator_description" rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Penjelasan rinci mengenai indikator ini..."></textarea>
          </div>

          <div>
            <label class="block mb-1 text-sm font-semibold text-gray-700">Deskripsi IRU (Indikator Risiko Utama)</label>
            <textarea v-model="form.iru_description" rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Penjelasan aspek risiko untuk IRU..."></textarea>
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="block mb-1 text-sm font-semibold text-gray-700">PIC Utama (Section)</label>
              <input v-model="form.pic_section" type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Cth: Dept. Keuangan" />
            </div>
            <div>
              <label class="block mb-1 text-sm font-semibold text-gray-700">Secondary PICs</label>
              <input v-model="form.secondary_pics" type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Pisahkan dengan koma jika lebih dari satu" />
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="block mb-1 text-sm font-semibold text-gray-700">P26 Initial Score (Batas Aman/Awal)</label>
              <input v-model="form.p26_initial" type="number" step="1"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Cth: 12" />
            </div>
            <div>
              <label class="block mb-1 text-sm font-semibold text-gray-700">R26 Initial Score (Batas Kritis)</label>
              <input v-model="form.r26_initial" type="number" step="1"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Cth: 20" />
            </div>
          </div>

          <div class="flex items-center pt-2">
            <input v-model="form.is_active" type="checkbox" id="is_active"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
            <label for="is_active" class="ml-2 text-sm font-medium text-gray-700">Indikator Aktif (Ditampilkan dalam
              perhitungan)</label>
          </div>

        </form>

        <div class="sticky bottom-0 z-10 flex justify-end gap-3 p-6 bg-white border-t border-gray-100 rounded-b-xl">
          <button type="button" @click="closeModal"
            class="px-4 py-2 text-sm font-medium text-gray-700 transition bg-gray-100 rounded-lg hover:bg-gray-200">Batal</button>
          <button type="submit" form="indicatorForm"
            class="px-4 py-2 text-sm font-medium text-white transition bg-blue-600 rounded-lg hover:bg-blue-700">Simpan
            Data</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api'; // Pastikan path utils/api menyesuaikan project Anda

const indicators = ref([]);
const isModalOpen = ref(false);

// State Form terpusat sesuai kolom DB
const form = ref({
  id: null,
  indicator_code: '',
  indicator_name: '',
  indicator_description: '',
  indicator_type: '',
  pic_section: '',
  secondary_pics: '',
  is_active: true,
  iru_description: '',
  p26_initial: null,
  r26_initial: null
});

// Load Data
const loadData = async () => {
  try {
    const res = await api.get('/admin/indicators');
    if (res.data?.data && Array.isArray(res.data.data)) {
      indicators.value = res.data.data.filter(item => item !== null && item !== undefined);
    }
  } catch (error) {
    console.error("Gagal menarik data indikator:", error);
  }
};

// Buka Modal & Inject Data
const openModal = (item = null) => {
  if (item) {
    // Mode Edit: Clone data ke form
    form.value = {
      id: item.id,
      indicator_code: item.indicator_code || '',
      indicator_name: item.indicator_name || '',
      indicator_description: item.indicator_description || '',
      indicator_type: item.indicator_type || '',
      pic_section: item.pic_section || '',
      secondary_pics: item.secondary_pics || '',
      is_active: item.is_active !== undefined ? item.is_active : true, // default true jika tidak ada field
      iru_description: item.iru_description || '',
      p26_initial: item.p26_initial !== undefined ? item.p26_initial : null,
      r26_initial: item.r26_initial !== undefined ? item.r26_initial : null
    };
  } else {
    // Mode Create: Kosongkan Form
    form.value = {
      id: null,
      indicator_code: '',
      indicator_name: '',
      indicator_description: '',
      indicator_type: '',
      pic_section: '',
      secondary_pics: '',
      is_active: true,
      iru_description: '',
      p26_initial: null,
      r26_initial: null
    };
  }
  isModalOpen.value = true;
};

// Tutup Modal
const closeModal = () => {
  isModalOpen.value = false;
};

// Simpan Data (Aksi Create / Update)
const saveData = async () => {
  try {
    const payload = { ...form.value };

    // Pastikan string kosong pada angka di-convert ke null untuk mencegah error constraint database
    if (payload.p26_initial === '') payload.p26_initial = null;
    if (payload.r26_initial === '') payload.r26_initial = null;

    if (form.value.id) {
      // Endpoint UPDATE (PUT/PATCH)
      await api.put(`/admin/indicators/${form.value.id}`, payload);
    } else {
      // Endpoint CREATE (POST)
      await api.post('/admin/indicators', payload);
    }

    await loadData(); // Reload table
    closeModal();
  } catch (error) {
    console.error("Gagal menyimpan indikator:", error);
    const msg = error.response?.data?.message || "Terjadi kesalahan saat menyimpan data. Periksa koneksi API Anda.";
    alert(msg);
  }
};

// Hapus Data (Aksi Delete)
const deleteIndicator = async (id) => {
  // Tambahkan verifikasi untuk menghindari penghapusan tidak disengaja
  if (confirm('Yakin ingin menghapus indikator ini? Menghapus indikator mungkin memengaruhi penilaian risiko terkait.')) {
    try {
      await api.delete(`/admin/indicators/${id}`);
      await loadData(); // Reload table
    } catch (error) {
      console.error("Gagal menghapus indikator:", error);
      const msg = error.response?.data?.message || "Gagal menghapus data. Pastikan indikator ini tidak sedang dipakai di tabel lain (Foreign Key Constraint).";
      alert(msg);
    }
  }
};

onMounted(() => {
  loadData();
});
</script>