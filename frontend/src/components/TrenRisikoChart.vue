<!-- ...\ManRiskMSKI\frontend\src\components\TrenRisikoChart.vue -->

<template>
  <div class="p-6 mt-8 bg-white border border-gray-100 shadow-sm rounded-xl">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-bold text-gray-800">Grafik Pergerakan Tren Risiko</h3>
        <p class="mt-1 text-xs text-gray-500">
          Pelacakan nilai risiko dari baseline awal tahun (P26) hingga target akhir tahun (R26).
        </p>
      </div>
      <div class="flex items-center gap-4 text-xs font-semibold text-gray-600">
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 bg-blue-600 rounded-full"></span> Nilai Aktual</span>
        <span class="flex items-center gap-1"><span class="inline-block w-3 h-3 border-2 border-red-400 border-dashed rounded-full"></span> Batas Aman (R26)</span>
      </div>
    </div>

    <div class="relative w-full h-72">
      <Line v-if="chartData.labels" :data="chartData" :options="chartOptions" />
      <div v-else class="absolute inset-0 flex items-center justify-center border border-gray-200 border-dashed rounded-lg bg-gray-50">
        <p class="text-sm font-medium text-gray-400 animate-pulse">Memuat data grafik...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'vue-chartjs';
import api from '@/utils/api';

// Daftarkan modul Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const props = defineProps({
  indicatorId: {
    type: [String, Number],
    required: true
  }
});

const chartData = ref({});

// 🚨 PERBAIKAN: cache pemetaan kategori/warna dari tabel risk_matrix_mapping di DB,
// dipakai untuk mewarnai titik grafik & label tooltip secara dinamis (pola yang sama
// dipakai di MatrixVisual.vue), bukan warna biru flat statis seperti sebelumnya.
const matrixMapping = ref([]);

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      min: 0,
      max: 25,
      ticks: { stepSize: 5 },
      title: { display: true, text: 'Skor Risiko Kemenkeu' },
      grid: { color: '#f1f5f9' }
    },
    x: {
      grid: { display: false }
    }
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1e293b',
      padding: 10,
      callbacks: {
        label: function(context) {
          const val = context.parsed.y;
          if (val === null || val === undefined) return ' Belum ada data';
          const cat = getCategoryForValue(val);
          return cat ? ` Skor Risiko: ${val} (${cat.category})` : ` Skor Risiko: ${val}`;
        }
      }
    }
  }
});

// Cari kategori & warna dari tabel risk_matrix_mapping berdasarkan risk_value,
// supaya warna titik grafik SELALU sinkron dengan definisi warna di database.
const getCategoryForValue = (value) => {
  if (value === null || value === undefined) return null;
  return matrixMapping.value.find(m => m.risk_value === value) || null;
};

// Ambil sekali saja data pemetaan matriks (jarang berubah), cache di matrixMapping.
const ensureMatrixMapping = async () => {
  if (matrixMapping.value.length) return;
  try {
    const res = await api.get('/matriks/mapping');
    if (res.data && res.data.status === 'success') {
      matrixMapping.value = res.data.data;
    }
  } catch (error) {
    console.error('Gagal memuat data mapping matriks untuk grafik tren:', error);
  }
};

const loadChartData = async () => {
  if (!props.indicatorId) return;

  try {
    await ensureMatrixMapping();

    // 🚨 PERBAIKAN: sebelumnya P26 & R26 di-hardcode (17 & 5) untuk SEMUA indikator
    // ("Asumsi Baseline ... Sesuaikan dengan logika bisnis KPPN Anda"). Padahal setiap
    // indikator sudah punya nilai p26_initial & r26_target MASING-MASING di tabel
    // risk_indicators, dan endpoint /risiko/indicators sudah mengembalikannya sebagai
    // field "p26" & "r26". Sekarang grafik selalu memakai baseline & target ASLI milik
    // indikator yang sedang ditampilkan, bukan angka tetap yang sama untuk semua indikator.
    const [indicatorsRes, assessmentsRes] = await Promise.all([
      api.get('/risiko/indicators'),
      api.get('/risiko/assessments')
    ]);

    const indicators = indicatorsRes.data.data || [];
    const indicator = indicators.find(i => Number(i.id) === Number(props.indicatorId));

    // Jika admin belum mengisi P26/R26 di database untuk indikator ini, biarkan null
    // (titik kosong / garis tidak tampil) daripada menampilkan angka palsu.
    const dataP26 = indicator?.p26 ?? null;
    const dataR26 = indicator?.r26 ?? null;

    const allData = assessmentsRes.data.data || [];

    // Filter data hanya untuk indikator yang dipilih
    const filtered = allData.filter(a => Number(a.indicator_id) === Number(props.indicatorId));

    // Siapkan array data untuk setiap titik (Fallback jika belum isi diatur ke null agar grafik terputus natural)
    const getScore = (q) => {
      const found = filtered.find(a => a.quarter === q);
      return found ? found.risk_value : null;
    };

    const dataQ1 = getScore('Q1');
    const dataQ2 = getScore('Q2');
    const dataQ3 = getScore('Q3');
    const dataQ4 = getScore('Q4');

    const actualPoints = [dataP26, dataQ1, dataQ2, dataQ3, dataQ4, dataR26];

    chartData.value = {
      labels: ['P26 (Baseline)', 'Q1', 'Q2', 'Q3', 'Q4', 'R26 (Target)'],
      datasets: [
        {
          label: 'Skor Risiko',
          data: actualPoints,
          borderColor: '#2563eb', // Blue-600
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          // 🚨 PERBAIKAN: warna tiap titik kini ikut kategori risk_matrix_mapping di DB
          // (Biru/Hijau Tua/Kuning/Oranye/Merah) berdasarkan skor risiko di titik itu,
          // bukan putih statis seperti sebelumnya.
          pointBackgroundColor: actualPoints.map(v => getCategoryForValue(v)?.color_code || '#ffffff'),
          pointBorderColor: '#2563eb',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7,
          fill: true,
          tension: 0.3, // Membuat garis sedikit melengkung (smooth)
          spanGaps: true // Menyambungkan garis meskipun ada data kuartal yang kosong (null)
        },
        {
          label: 'Garis Target R26',
          // 🚨 PERBAIKAN: garis batas aman sekarang memakai r26_target ASLI indikator ini
          // (bukan hardcode 5 untuk semua indikator seperti sebelumnya)
          data: [dataR26, dataR26, dataR26, dataR26, dataR26, dataR26],
          borderColor: '#f87171', // Red-400
          borderDash: [5, 5], // Garis putus-putus
          pointRadius: 0,
          fill: false,
          tension: 0,
          spanGaps: true
        }
      ]
    };
  } catch (error) {
    console.error("Gagal memuat data grafik tren:", error);
  }
};

// Pantau perubahan properti (saat user mengganti pilihan dropdown indikator)
watch(() => props.indicatorId, () => {
  loadChartData();
}, { immediate: true });
</script>