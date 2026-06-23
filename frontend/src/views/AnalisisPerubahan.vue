<!-- ...\ManRiskMSKI\frontend\src\views\AnalisisPerubahan.vue -->

<template>
  <div class="p-6 mx-auto space-y-8 max-w-7xl">
    
    <div class="p-6 bg-white border border-gray-100 shadow-sm rounded-xl">
      <h2 class="text-3xl font-bold tracking-tight text-gray-900">Analisis Perubahan & Tren Risiko</h2>
      <p class="mt-1 text-sm text-gray-500">
        Bandingkan matriks peta risiko antar-periode secara berdampingan untuk melacak pergerakan dan pemenuhan target mitigasi.
      </p>
    </div>

    <div class="grid grid-cols-1 gap-6 p-6 bg-white border border-gray-100 shadow-sm rounded-xl md:grid-cols-3">
      <div>
        <label for="indicator-select" class="block mb-2 text-sm font-semibold text-gray-700">Pilih Indikator Risiko:</label>
        <select 
          id="indicator-select"
          v-model="selectedIndicatorId" 
          @change="calculateMovement"
          class="w-full px-4 py-2 text-sm text-gray-700 transition bg-white border border-gray-300 rounded-lg shadow-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="" disabled>-- Pilih Indikator Risiko --</option>
          
          <option v-for="item in indicators" :key="item?.id" :value="item?.id">
  {{ item?.code }} - {{ item?.iru || item?.name }}
</option>
        </select>
      </div>

      <div>
        <label id="period-a-label" class="block mb-2 text-sm font-semibold text-gray-700">Periode Asal (Kiri):</label>
        <select 
          v-model="periodA" 
          @change="calculateMovement"
          aria-labelledby="period-a-label"
          class="w-full px-4 py-2 text-sm text-gray-700 transition bg-white border border-gray-300 rounded-lg shadow-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="P26">Baseline P26 (Awal Tahun)</option>
          <option value="Q1">Triwulan 1</option>
          <option value="Q2">Triwulan 2</option>
          <option value="Q3">Triwulan 3</option>
          <option value="Q4">Triwulan 4</option>
        </select>
      </div>

      <div>
        <label id="period-b-label" class="block mb-2 text-sm font-semibold text-gray-700">Periode Pembanding (Kanan):</label>
        <select 
          v-model="periodB" 
          @change="calculateMovement"
          aria-labelledby="period-b-label"
          class="w-full px-4 py-2 text-sm text-gray-700 transition bg-white border border-gray-300 rounded-lg shadow-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="Q1">Triwulan 1</option>
          <option value="Q2">Triwulan 2</option>
          <option value="Q3">Triwulan 3</option>
          <option value="Q4">Triwulan 4</option>
          <option value="R26">Target R26 (Batas Aman)</option>
        </select>
      </div>
    </div>

    <div v-if="!selectedIndicatorId" class="p-12 font-medium text-center text-gray-400 border border-gray-300 border-dashed bg-gray-50 rounded-xl">
      ⚠️ Silakan pilih indikator risiko terlebih dahulu untuk melihat visualisasi perbandingan tren.
    </div>

    <div v-else class="grid items-start grid-cols-1 gap-8 lg:grid-cols-2">
      
      <div class="flex flex-col items-center p-6 bg-white border border-gray-100 shadow-sm rounded-xl">
        <div class="mb-4 text-center">
          <span class="px-3 py-1 text-xs font-bold tracking-wider text-blue-800 uppercase bg-blue-100 rounded-full">
            Periode: {{ periodA }}
          </span>
          <h4 class="mt-2 text-sm font-bold text-gray-700">
            Posisi Risiko: <span v-if="posA.valid" class="font-mono text-blue-600">Skor {{ posA.score }} (F:{{ posA.f }}, D:{{ posA.imp }})</span>
            <span v-else class="italic text-gray-400">Belum Diinput</span>
          </h4>
        </div>

        <div class="grid grid-cols-5 gap-1 p-2 bg-gray-100 border border-gray-200 rounded-lg">
          <template v-for="freq in reversedYAxis" :key="'grid-a-f-'+freq">
            <div 
              v-for="impact in xAxis" 
              :key="'grid-a-cell-'+freq+'-'+impact"
              class="flex items-center justify-center w-10 h-10 font-mono text-xs font-bold transition-all rounded sm:w-12 sm:h-12"
              :class="[
                getMatriksColorClass(freq, impact),
                isCellActive(posA, freq, impact) ? 'ring-4 ring-black scale-105 z-10 shadow-md border-2 border-white' : 'opacity-40'
              ]"
            >
              {{ getOfficialValue(freq, impact) }}
              <span v-if="isCellActive(posA, freq, impact)" class="absolute -top-1 -left-1 bg-black text-white text-[8px] px-1 rounded-sm">ORIGIN</span>
            </div>
          </template>
        </div>
      </div>

      <div class="flex flex-col items-center p-6 bg-white border border-gray-100 shadow-sm rounded-xl">
        <div class="mb-4 text-center">
          <span class="px-3 py-1 text-xs font-bold tracking-wider text-purple-800 uppercase bg-purple-100 rounded-full">
            Periode: {{ periodB }}
          </span>
          <h4 class="mt-2 text-sm font-bold text-gray-700">
            Posisi Risiko: <span v-if="posB.valid" class="font-mono text-purple-600">Skor {{ posB.score }} (F:{{ posB.f }}, D:{{ posB.imp }})</span>
            <span v-else class="italic text-gray-400">Belum Diinput</span>
          </h4>
        </div>

        <div class="grid grid-cols-5 gap-1 p-2 bg-gray-100 border border-gray-200 rounded-lg">
          <template v-for="freq in reversedYAxis" :key="'grid-b-f-'+freq">
            <div 
              v-for="impact in xAxis" 
              :key="'grid-b-cell-'+freq+'-'+impact"
              class="relative flex flex-col items-center justify-center w-10 h-10 font-mono text-xs font-bold transition-all rounded sm:w-12 sm:h-12"
              :class="[
                getMatriksColorClass(freq, impact),
                isCellActive(posB, freq, impact) ? 'ring-4 ring-purple-700 scale-105 z-10 shadow-md border-2 border-white' : '',
                !isCellActive(posB, freq, impact) && isCellActive(posA, freq, impact) ? 'border-2 border-dashed border-gray-500 opacity-60' : '',
                !isCellActive(posB, freq, impact) && !isCellActive(posA, freq, impact) ? 'opacity-40' : ''
              ]"
            >
              <span>{{ getOfficialValue(freq, impact) }}</span>
              
              <span v-if="!isCellActive(posB, freq, impact) && isCellActive(posA, freq, impact)" class="absolute text-[9px] bg-gray-700 text-white p-0.5 rounded scale-70">ASAL</span>
              
              <span v-if="isCellActive(posB, freq, impact)" class="absolute -top-1 -right-1 bg-purple-700 text-white text-[8px] px-1 rounded-sm">TARGET</span>
              
              <span v-if="isCellActive(posB, freq, impact) && hasMoved" class="text-[10px] mt-0.5 animate-bounce" aria-hidden="true">
                {{ getMovementArrowIcon() }}
              </span>
            </div>
          </template>
        </div>
      </div>

    </div>

    <div v-if="selectedIndicatorId" class="flex flex-col items-start justify-between gap-4 p-6 text-white bg-gray-900 shadow-md rounded-xl sm:flex-row sm:items-center">
      <div class="space-y-1">
        <h4 class="text-xs font-bold tracking-widest text-gray-400 uppercase">Kesimpulan Analisis Tren</h4>
        <p class="text-lg font-medium leading-relaxed">
          Peralihan dari <span :class="getTextColorClass(posA.color)">{{ posA.category || 'Belum Ada Data' }} (Skor {{ posA.score || 0 }})</span> 
          menuju <span :class="getTextColorClass(posB.color)">{{ posB.category || 'Belum Ada Data' }} (Skor {{ posB.score || 0 }})</span>.
        </p>
        <p class="text-sm text-gray-300 font-mono mt-2 bg-gray-800 p-2.5 rounded-lg border border-gray-700 inline-block">
          Status Pergerakan: <strong>{{ movementStatusText }}</strong>
        </p>
      </div>

      <div class="px-5 py-4 text-center bg-white border border-white shrink-0 bg-opacity-10 rounded-xl border-opacity-10">
        <span class="block mb-1 text-3xl" aria-hidden="true">{{ isTargetAchieved ? '🎉' : '⚠️' }}</span>
        <span class="block text-xs font-bold tracking-wider uppercase" :class="isTargetAchieved ? 'text-green-400' : 'text-yellow-400'">
          {{ isTargetAchieved ? 'Target Tercapai ✓' : 'Perlu Atensi Mitgasi' }}
        </span>
      </div>
    </div>

    <div v-if="selectedIndicatorId" class="flex flex-col items-start justify-between gap-4 p-6 text-white bg-gray-900 shadow-md rounded-xl sm:flex-row sm:items-center">
      </div>

    <TrenRisikoChart 
      v-if="selectedIndicatorId" 
      :indicator-id="selectedIndicatorId" 
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api';
import TrenRisikoChart from '@/components/TrenRisikoChart.vue';

const xAxis = [1, 2, 3, 4, 5];
const reversedYAxis = [5, 4, 3, 2, 1];

const indicators = ref([]);
const allAssessments = ref([]);

const selectedIndicatorId = ref('');
const periodA = ref('Q1');
const periodB = ref('Q2');

// State Posisi Koordinat Sel
const posA = ref({ f: 0, imp: 0, score: 0, category: '', color: '', valid: false });
const posB = ref({ f: 0, imp: 0, score: 0, category: '', color: '', valid: false });
const hasMoved = ref(false);
const isTargetAchieved = ref(false);
const movementStatusText = ref('Stabil');

// Layout Matriks Resmi Kemenkeu Pola 5x5 dari T01
const officialMatrixLayout = {
  5: { 1: 9, 2: 15, 3: 18, 4: 23, 5: 25 },
  4: { 1: 6, 2: 12, 3: 16, 4: 19, 5: 24 },
  3: { 1: 4, 2: 10, 3: 14, 4: 17, 5: 22 },
  2: { 1: 2, 2: 7,  3: 11, 4: 13, 5: 21 },
  1: { 1: 1, 2: 3,  3: 5,  4: 8,  5: 20 }
};

const getOfficialValue = (freq, impact) => officialMatrixLayout[freq]?.[impact] || 0;

const getCategoryByScore = (score) => {
  if (score === 0) return { name: 'Kosong', color: 'Kelabu' };
  if (score <= 5) return { name: 'Risiko Rendah', color: 'Biru' };
  if (score <= 11) return { name: 'Risiko Sedang Rendah', color: 'Hijau' };
  if (score <= 15) return { name: 'Risiko Sedang', color: 'Kuning' };
  if (score <= 19) return { name: 'Risiko Tinggi', color: 'Jingga' };
  return { name: 'Risiko Sangat Tinggi', color: 'Merah' };
};

const getMatriksColorClass = (freq, impact) => {
  const score = getOfficialValue(freq, impact);
  if (score <= 5) return 'bg-blue-500 text-white';
  if (score <= 11) return 'bg-green-500 text-white';
  if (score <= 15) return 'bg-yellow-400 text-yellow-950';
  if (score <= 19) return 'bg-orange-500 text-white';
  return 'bg-red-600 text-white';
};

const getTextColorClass = (color) => {
  const map = {
    'Birid': 'text-blue-400 font-bold',
    'Hijau': 'text-green-400 font-bold',
    'Kuning': 'text-yellow-400 font-bold',
    'Jingga': 'text-orange-400 font-bold',
    'Merah': 'text-red-400 font-bold'
  };
  return map[color] || 'text-white';
};

const isCellActive = (posObj, freq, impact) => {
  return posObj.valid && posObj.f === freq && posObj.imp === impact;
};

// Menentukan arah panah ringkas berdasarkan perubahan nilai skor
const getMovementArrowIcon = () => {
  if (posB.value.score < posA.value.score) return '📉 ⬇️';
  if (posB.value.score > posA.value.score) return '📈 ⬆️';
  return '➡️';
};

// Simulasi data Target Baseline historis jika data kosong di DB (Fallback Perlindungan T25)
const getFallbackPeriodData = (period, indicatorId) => {
  // P26 Baseline rencana awal tahun biasanya berada di area sedang/tinggi
  if (period === 'P26') {
    return { frequency: 3, impact: 4, score: 17, category: 'Risiko Tinggi', color: 'Jingga', valid: true };
  }
  // R26 Target akhir tahun wajib di area aman (Rendah / Sedang Rendah)
  if (period === 'R26') {
    return { frequency: 1, impact: 3, score: 5, category: 'Risiko Rendah', color: 'Biru', valid: true };
  }
  return { frequency: 0, impact: 0, score: 0, category: '', color: '', valid: false };
};

const calculateMovement = () => {
  if (!selectedIndicatorId.value) return;

  // 1. Ekstrak Posisi A
  const dataA = allAssessments.value.find(a => a.indicator_id === selectedIndicatorId.value && a.quarter === periodA.value);
  if (dataA) {
    posA.value = {
      f: dataA.frequency || 3, // Fallback jika tidak terdefinisi lengkap
      imp: dataA.impact || 3,
      score: dataA.risk_value,
      category: dataA.risk_category || getCategoryByScore(dataA.risk_value).name,
      color: getCategoryByScore(dataA.risk_value).color,
      valid: true
    };
  } else {
    // Ambil dari skenario baseline statis jika data transaksi quarter tidak ditemukan
    const fallback = getFallbackPeriodData(periodA.value, selectedIndicatorId.value);
    posA.value = fallback.valid ? fallback : { f: 0, imp: 0, score: 0, category: 'Belum Isi', color: 'Kelabu', valid: false };
  }

  // 2. Ekstrak Posisi B
  const dataB = allAssessments.value.find(a => a.indicator_id === selectedIndicatorId.value && a.quarter === periodB.value);
  if (dataB) {
    posB.value = {
      f: dataB.frequency || 2,
      imp: dataB.impact || 2,
      score: dataB.risk_value,
      category: dataB.risk_category || getCategoryByScore(dataB.risk_value).name,
      color: getCategoryByScore(dataB.risk_value).color,
      valid: true
    };
  } else {
    const fallback = getFallbackPeriodData(periodB.value, selectedIndicatorId.value);
    posB.value = fallback.valid ? fallback : { f: 0, imp: 0, score: 0, category: 'Belum Isi', color: 'Kelabu', valid: false };
  }

  // 3. Hitung Evaluasi Perubahan & Status Keberhasilan Capaian
  if (posA.value.valid && posB.value.valid) {
    hasMoved.value = (posA.value.f !== posB.value.f) || (posA.value.imp !== posB.value.imp);
    
    if (posB.value.score < posA.value.score) {
      movementStatusText.value = `Risiko Menurun (Positif) — Berhasil Turun ${posA.value.score - posB.value.score} Poin`;
      isTargetAchieved.value = true;
    } else if (posB.value.score > posA.value.score) {
      movementStatusText.value = `Risiko Meningkat (Negatif) — Naik ${posB.value.score - posA.value.score} Poin`;
      isTargetAchieved.value = false;
    } else {
      movementStatusText.value = 'Risiko Stabil (Konstan)';
      // Jika stabil di area hijau/biru dianggap tetap aman
      isTargetAchieved.value = (posB.value.score <= 11);
    }
  } else {
    hasMoved.value = false;
    isTargetAchieved.value = false;
    movementStatusText.value = 'Data Tidak Lengkap';
  }
};

const loadInitialData = async () => {
  try {
    const indRes = await api.get('/risiko/indicators');
    
    // Pastikan data adalah array dan filter elemen yang null/undefined
    if (indRes.data?.data && Array.isArray(indRes.data.data)) {
      indicators.value = indRes.data.data.filter(item => item !== null && item !== undefined);
    }

    const assRes = await api.get('/risiko/assessments');
    if (assRes.data?.data && Array.isArray(assRes.data.data)) {
      allAssessments.value = assRes.data.data.filter(item => item !== null && item !== undefined);
    }
  } catch (error) {
    console.error("Gagal menarik data komparasi analitis:", error);
  }
};

onMounted(() => {
  loadInitialData();
});
</script>

<style scoped>
/* Animasi kedip lembut untuk sel penanda target mitigasi baru */
.animate-bounce {
  animation: bounce 1.2s infinite;
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}
</style>