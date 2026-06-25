<!-- ...\ManRiskMSKI\frontend\src\views\DashboardPage.vue -->

<template>
  <div class="p-6 mx-auto space-y-8 max-w-7xl">

    <div
      class="flex flex-col items-start justify-between gap-4 p-6 bg-white border border-gray-100 shadow-sm sm:flex-row sm:items-center rounded-xl">
      <div>
        <div class="flex items-center gap-2">
          <h2 class="text-3xl font-bold tracking-tight text-gray-900">Dashboard Risiko KPPN</h2>
          <span class="relative flex w-2 h-2 mt-1">
            <span class="absolute inline-flex w-full h-full bg-green-400 rounded-full opacity-75 animate-ping"></span>
            <span class="relative inline-flex w-2 h-2 bg-green-500 rounded-full"></span>
          </span>
        </div>
        <p class="mt-1 text-sm text-gray-500">
          Pemantauan real-time sebaran komponen dari <strong>25 Indikator Risiko Utama</strong>.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <label for="quarter-select" class="text-sm font-semibold text-gray-700">Periode:</label>
        <select id="quarter-select" v-model="selectedQuarter" @change="loadDashboardData"
          class="px-4 py-2 font-medium text-gray-700 transition bg-white border border-gray-300 rounded-lg shadow-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
          <option value="Q1">Triwulan 1 (Jan - Mar)</option>
          <option value="Q2">Triwulan 2 (Apr - Jun)</option>
          <option value="Q3">Triwulan 3 (Jul - Sep)</option>
          <option value="Q4">Triwulan 4 (Okt - Des)</option>
        </select>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
      <div v-for="color in orderedColors" :key="color"
        class="flex flex-col justify-between p-5 text-center transition-transform shadow-sm rounded-xl hover:scale-105"
        :style="getCategoryStyle(color)">
        <h3 class="text-xs font-bold tracking-wider uppercase opacity-90" :class="getCardTextClass(color)">{{ getDescriptiveName(color) }}</h3>
        <p class="my-2 text-4xl font-extrabold" :class="getCardTextClass(color)">{{ summary[color] || 0 }}</p>
        <span class="text-[10px] bg-white bg-opacity-20 px-2 py-0.5 rounded-full mx-auto font-medium" :class="getCardTextClass(color)">
          {{ getLegendSymbol(color) }} Kategori {{ color }}
        </span>
      </div>
    </div>

    <div class="space-y-8">

      <div class="flex items-center justify-center p-6 bg-white border border-gray-100 shadow-sm rounded-xl">
        <div class="w-full max-w-4xl">
          <MatrixVisual />
        </div>
      </div>

      <div class="overflow-hidden bg-white border border-gray-100 shadow-sm rounded-xl">
        <div class="flex items-center justify-between p-6 border-b border-gray-100 bg-gray-50">
          <div>
            <h3 class="text-lg font-bold text-gray-800">Daftar & Deskripsi Indikator Risiko Resmi Kemenkeu</h3>
            <p class="text-xs text-gray-500 mt-0.5">Menampilkan rincian kode, deskripsi indikator secara lengkap, serta
              penugasan seksi PIC.</p>
          </div>
          <span class="px-3 py-1 text-xs font-bold text-blue-800 bg-blue-100 rounded-full">
            Total: {{ indicators.length }} Indikator Aktif
          </span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 z-10 bg-white border-b shadow-sm">
              <tr>
                <th class="w-24 p-4 pl-6 text-xs font-bold tracking-wider text-gray-500 uppercase">Kode</th>
                <th class="p-4 pl-6 text-xs font-bold tracking-wider text-gray-500 uppercase">IRU</th>
                <th class="p-4 text-xs font-bold tracking-wider text-gray-500 uppercase">Deskripsi Indikator Risiko</th>
                <th class="w-40 p-4 text-xs font-bold tracking-wider text-center text-gray-500 uppercase">PIC Utama</th>
                <th class="p-4 text-xs font-bold tracking-wider text-center text-gray-500 uppercase w-44">PIC Pendamping
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-100">
              <tr v-for="item in filteredIndicators" :key="item.id" class="transition-colors hover:bg-gray-50">

                <td class="p-4 font-mono text-sm font-bold text-blue-600 whitespace-nowrap">
                  {{ item.code }}
                </td>

                <td class="p-4 pl-6 text-sm font-medium leading-relaxed text-gray-700">
                  {{ item.iru || 'Belum diatur' }}
                </td>

                <td class="p-4 pr-4 text-sm font-medium leading-relaxed text-gray-700">
                  {{ item.kejadian_risiko || '-' }}
                </td>

                <td class="p-4 text-center">
                  <span
                    class="inline-block bg-blue-50 text-blue-800 font-semibold px-2.5 py-1 rounded-md text-xs border border-blue-200 whitespace-nowrap">
                    👤 {{ item.pic || '-' }}
                  </span>
                </td>

                <td class="p-4 text-center">
                  <span v-if="item.secondary_pics"
                    class="inline-block bg-purple-50 text-purple-800 font-semibold px-2.5 py-1 rounded-md text-xs border border-purple-200 whitespace-nowrap">
                    🤝 {{ item.secondary_pics }}
                  </span>
                  <span v-else class="text-xs italic text-gray-400">-</span>
                </td>
              </tr>

              <tr v-if="filteredIndicators.length === 0">
                <td colspan="5" class="p-12 font-medium text-center text-gray-400">
                  <span v-if="indicators.length === 0">🔄 Sedang memuat data indikator risiko...</span>
                  <span v-else>Tidak ada data indikator yang ditugaskan ke seksi Anda.</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
// import { ref, onMounted, onUnmounted } from 'vue';
// import { ref, computed, onMounted } from 'vue';
import { ref, computed, onMounted, onUnmounted } from 'vue';
import api from '@/utils/api';
import MatrixVisual from '@/components/MatrixVisual.vue';
// 🚨 PERBAIKAN: authStore dipakai di computed filteredIndicators tapi belum diimpor.
// Sesuaikan path/nama export di bawah ini dengan store auth Sandy yang sebenarnya.
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();
const indicators = ref([]);

// 🚨 PERBAIKAN: sebelumnya kategori, warna, label, & simbol di-hardcode
// ('Biru','Hijau','Kuning','Jingga','Merah'). Setelah data risk_matrix_mapping
// di database diperbarui, nama kategori yang sebenarnya jadi 'Hijau Tua' & 'Oranye'
// (bukan 'Hijau' & 'Jingga') — akibatnya 2 kartu ini TIDAK PERNAH menampilkan
// hitungan yang benar walau datanya ada. Sekarang seluruh kategori, warna, deskripsi,
// dan urutan kartu diambil langsung dari tabel risk_matrix_mapping via /matriks/mapping,
// jadi akan SELALU ikut menyesuaikan kalau suatu saat kategori di database diubah lagi.
const categoryMeta = ref([]); // [{ category, color_code, description, mitigation_level, risk_value (min) }]
const orderedColors = computed(() => categoryMeta.value.map(c => c.category));

const summary = ref({});
const selectedQuarter = ref('Q1');
let autoRefreshInterval = null;

const getCategoryInfo = (color) => categoryMeta.value.find(c => c.category === color);

const getDescriptiveName = (color) => {
  const info = getCategoryInfo(color);
  return info ? info.description : color;
};

// Style background diambil langsung dari color_code di database (bukan kelas Tailwind statis)
const getCategoryStyle = (color) => {
  const info = getCategoryInfo(color);
  return { backgroundColor: info ? info.color_code : '#4B5563' };
};

// Cek kontras warna background (YIQ) supaya teks tetap terbaca,
// terutama untuk warna terang seperti Kuning (#FFFF00).
const getCardTextClass = (color) => {
  const info = getCategoryInfo(color);
  if (!info || !info.color_code) return 'text-white';
  const hex = info.color_code.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return yiq >= 128 ? 'text-gray-900' : 'text-white';
};

const getLegendSymbol = (color) => {
  const lower = color.toLowerCase();
  if (lower.includes('hijau')) return '▲';
  if (lower.includes('kuning')) return '■';
  if (lower.includes('oranye') || lower.includes('jingga')) return '◆';
  if (lower.includes('merah')) return '★';
  return '●';
};

// Ambil daftar kategori unik (+ warna, deskripsi, level mitigasi) dari database
const loadMatrixCategories = async () => {
  try {
    const res = await api.get('/matriks/mapping');
    if (res.data && res.data.data) {
      const map = new Map();
      res.data.data.forEach(item => {
        const existing = map.get(item.category);
        // Simpan baris dengan risk_value PALING RENDAH per kategori sbg representasi
        // (warna/deskripsi tetap sama per kategori, hanya dipakai utk urutan kartu).
        if (!existing || item.risk_value < existing.risk_value) {
          map.set(item.category, {
            category: item.category,
            color_code: item.color_code,
            description: item.description,
            mitigation_level: item.mitigation_level,
            risk_value: item.risk_value
          });
        }
      });
      categoryMeta.value = Array.from(map.values()).sort((a, b) => a.risk_value - b.risk_value);
    }
  } catch (error) {
    console.error('Gagal memuat kategori matriks dari database:', error);
  }
};

const loadDashboardData = async () => {
  try {
    const currentYear = new Date().getFullYear();
    const summaryRes = await api.get(`/dashboard/summary?quarter=${selectedQuarter.value}&year=${currentYear}`);
    if (summaryRes.data && summaryRes.data.data) {
      // Pastikan semua kategori yang ada di DB tetap tampil (default 0) walau
      // belum ada asesmen utk kategori tersebut pada periode ini.
      const base = {};
      categoryMeta.value.forEach(c => { base[c.category] = 0; });
      summary.value = { ...base, ...summaryRes.data.data };
    }
  } catch (error) {
    console.error("Gagal memuat data ringkasan kartu berkala:", error);
  }

  try {
    const indicatorsRes = await api.get('/risiko/indicators');
    if (indicatorsRes.data && indicatorsRes.data.data) {
      indicators.value = indicatorsRes.data.data;
    }
  } catch (error) {
    console.error("Gagal mengambil daftar indikator.", error);
  }
};

// FUNGSI BARU: Memfilter indikator berdasarkan Role dan Seksi User
const filteredIndicators = computed(() => {
  const userRole = authStore.user?.role;
  const userSection = authStore.user?.section;

  if (userRole === 'admin') {
    return indicators.value;
  }

  return indicators.value.filter(item => {
    const isPrimary = item.pic === userSection;
    const isSecondary = item.secondary_pics && item.secondary_pics.includes(userSection);
    return isPrimary || isSecondary;
  });
});

onMounted(async () => {
  await loadMatrixCategories();
  loadDashboardData();

  autoRefreshInterval = setInterval(() => {
    loadDashboardData();
  }, 30000);
});

onUnmounted(() => {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
  }
});
</script>

<style scoped>
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>