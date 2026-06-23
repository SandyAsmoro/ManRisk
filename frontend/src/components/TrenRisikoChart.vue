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
import { ref, watch, onMounted } from 'vue';
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
          return ` Skor Risiko: ${context.parsed.y}`;
        }
      }
    }
  }
});

const loadChartData = async () => {
  if (!props.indicatorId) return;

  try {
    const res = await api.get('/risiko/assessments');
    const allData = res.data.data || [];
    
    // Filter data hanya untuk indikator yang dipilih
    const filtered = allData.filter(a => a.indicator_id === props.indicatorId);

    // Siapkan array data untuk setiap titik (Fallback jika belum isi diatur ke null agar grafik terputus natural)
    const getScore = (q) => {
      const found = filtered.find(a => a.quarter === q);
      return found ? found.risk_value : null;
    };

    const dataQ1 = getScore('Q1');
    const dataQ2 = getScore('Q2');
    const dataQ3 = getScore('Q3');
    const dataQ4 = getScore('Q4');

    // Asumsi Baseline: P26 (17) dan R26 (5) - Sesuaikan dengan logika bisnis KPPN Anda
    const dataP26 = 17; 
    const dataR26 = 5;  

    chartData.value = {
      labels: ['P26 (Baseline)', 'Q1', 'Q2', 'Q3', 'Q4', 'R26 (Target)'],
      datasets: [
        {
          label: 'Skor Risiko',
          data: [dataP26, dataQ1, dataQ2, dataQ3, dataQ4, dataR26],
          borderColor: '#2563eb', // Blue-600
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          pointBackgroundColor: '#ffffff',
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
          data: [5, 5, 5, 5, 5, 5], // Garis lurus di angka 5 (Risiko Rendah)
          borderColor: '#f87171', // Red-400
          borderDash: [5, 5], // Garis putus-putus
          pointRadius: 0,
          fill: false,
          tension: 0
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