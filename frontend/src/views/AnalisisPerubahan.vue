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
              :style="getCellStyle(freq, impact)"
              :class="[
                getCellTextClass(freq, impact),
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
              :style="getCellStyle(freq, impact)"
              :class="[
                getCellTextClass(freq, impact),
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
          Peralihan dari <span class="font-bold" :style="{ color: lightenForDarkBg(posA.color_code) }">{{ posA.category || 'Belum Ada Data' }} (Skor {{ posA.score || 0 }})</span> 
          menuju <span class="font-bold" :style="{ color: lightenForDarkBg(posB.color_code) }">{{ posB.category || 'Belum Ada Data' }} (Skor {{ posB.score || 0 }})</span>.
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
const matrixData = ref([]); // 🚨 Satu-satunya sumber kebenaran utk layout matriks, dari /matriks/mapping

const selectedIndicatorId = ref('');
const periodA = ref('Q1');
const periodB = ref('Q2');

// State Posisi Koordinat Sel
const posA = ref({ f: 0, imp: 0, score: 0, category: '', color: '', color_code: '#9CA3AF', valid: false });
const posB = ref({ f: 0, imp: 0, score: 0, category: '', color: '', color_code: '#9CA3AF', valid: false });
const hasMoved = ref(false);
const isTargetAchieved = ref(false);
const movementStatusText = ref('Stabil');

// 🚨 PERBAIKAN: sebelumnya 'officialMatrixLayout' di-hardcode di kode (mis. Frekuensi=1,
// Dampak=2 ditulis manual = 3), padahal data terbaru di tabel risk_matrix_mapping bilang
// kombinasi itu nilainya 5. Hardcode ini akan langsung basi setiap kali isi tabel diubah.
// Sekarang nilai sel SELALU dicari langsung dari data yang diambil dari /matriks/mapping.
const getCellInfo = (freq, impact) =>
  matrixData.value.find(item => item.frequency === freq && item.impact === impact) || null;

const getOfficialValue = (freq, impact) => getCellInfo(freq, impact)?.risk_value ?? 0;

// Cari baris kategori resmi di tabel matriks berdasarkan skor risiko aktual (bukan ambang hardcode lagi)
const getCellInfoByScore = (score) =>
  matrixData.value.find(item => item.risk_value === score) || null;

// Background sel grid diambil langsung dari color_code di database
const getCellStyle = (freq, impact) => {
  const cell = getCellInfo(freq, impact);
  return { backgroundColor: cell ? cell.color_code : '#D1D5DB' };
};

// Warna teks sel disesuaikan otomatis (kontras YIQ) terhadap warna background dari database
const getCellTextClass = (freq, impact) => {
  const cell = getCellInfo(freq, impact);
  if (!cell || !cell.color_code) return 'text-gray-700';
  const hex = cell.color_code.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return yiq >= 128 ? 'text-gray-900' : 'text-white';
};

const isCellActive = (posObj, freq, impact) => {
  return posObj.valid && posObj.f === freq && posObj.imp === impact;
};

// Kotak kesimpulan punya background gelap (bg-gray-900). Warna asli dari database
// (mis. Hijau Tua #006600) bisa terlalu gelap utk dibaca di atas background gelap,
// jadi dicerahkan sedikit secara otomatis — tetap mengikuti hue dari database,
// hanya disesuaikan agar kontras terhadap bg-gray-900 tetap terjaga.
const lightenForDarkBg = (hex, amount = 0.45) => {
  if (!hex) return '#FFFFFF';
  const clean = hex.replace('#', '');
  const r = parseInt(clean.substr(0, 2), 16);
  const g = parseInt(clean.substr(2, 2), 16);
  const b = parseInt(clean.substr(4, 2), 16);
  const lr = Math.round(r + (255 - r) * amount);
  const lg = Math.round(g + (255 - g) * amount);
  const lb = Math.round(b + (255 - b) * amount);
  return `rgb(${lr}, ${lg}, ${lb})`;
};

// Menentukan arah panah ringkas berdasarkan perubahan nilai skor
const getMovementArrowIcon = () => {
  if (posB.value.score < posA.value.score) return '📉 ⬇️';
  if (posB.value.score > posA.value.score) return '📈 ⬆️';
  return '➡️';
};

// 🚨 PERBAIKAN: sebelumnya fallback P26/R26 SELALU pakai angka simulasi tetap
// (Skor 17 utk semua P26, Skor 5 utk semua R26) tidak peduli indikator mana yang
// dipilih. Sekarang ambil nilai p26/r26 ASLI milik indikator yang sedang dipilih
// (kolom p26_initial/r26_target di database), lalu cari koordinat & kategori
// resminya di tabel matriks berdasarkan skor tersebut.
const getFallbackPeriodData = (period, indicatorId) => {
  const indicator = indicators.value.find(i => i?.id === indicatorId);
  const score = indicator ? (period === 'P26' ? indicator.p26 : period === 'R26' ? indicator.r26 : null) : null;

  if (score === null || score === undefined) {
    return { frequency: 0, impact: 0, score: 0, category: '', color: '', color_code: '#9CA3AF', valid: false };
  }

  const cell = getCellInfoByScore(score);
  return {
    frequency: cell?.frequency ?? 0,
    impact: cell?.impact ?? 0,
    score,
    category: cell?.description ?? 'Tidak diketahui',
    color: cell?.category ?? '',
    color_code: cell?.color_code ?? '#9CA3AF',
    valid: true
  };
};

const calculateMovement = () => {
  if (!selectedIndicatorId.value) return;

  // 1. Ekstrak Posisi A
  const dataA = allAssessments.value.find(a => a.indicator_id === selectedIndicatorId.value && a.quarter === periodA.value);
  if (dataA) {
    const cellInfo = getCellInfoByScore(dataA.risk_value);
    posA.value = {
      f: dataA.frequency,
      imp: dataA.impact,
      score: dataA.risk_value,
      category: dataA.risk_category || cellInfo?.description || 'Tidak diketahui',
      color: dataA.risk_category || cellInfo?.category || '',
      color_code: cellInfo?.color_code || '#9CA3AF',
      valid: true
    };
  } else {
    // Ambil dari skenario baseline P26/R26 ASLI milik indikator ini jika data transaksi quarter tidak ditemukan
    const fallback = getFallbackPeriodData(periodA.value, selectedIndicatorId.value);
    posA.value = fallback.valid ? fallback : { f: 0, imp: 0, score: 0, category: 'Belum Isi', color: 'Kelabu', color_code: '#9CA3AF', valid: false };
  }

  // 2. Ekstrak Posisi B
  const dataB = allAssessments.value.find(a => a.indicator_id === selectedIndicatorId.value && a.quarter === periodB.value);
  if (dataB) {
    const cellInfo = getCellInfoByScore(dataB.risk_value);
    posB.value = {
      f: dataB.frequency,
      imp: dataB.impact,
      score: dataB.risk_value,
      category: dataB.risk_category || cellInfo?.description || 'Tidak diketahui',
      color: dataB.risk_category || cellInfo?.category || '',
      color_code: cellInfo?.color_code || '#9CA3AF',
      valid: true
    };
  } else {
    const fallback = getFallbackPeriodData(periodB.value, selectedIndicatorId.value);
    posB.value = fallback.valid ? fallback : { f: 0, imp: 0, score: 0, category: 'Belum Isi', color: 'Kelabu', color_code: '#9CA3AF', valid: false };
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
      // Jika stabil, anggap aman bila level mitigasi resmi dari database tergolong rendah
      // (Low / Low-Medium) — bukan ambang skor hardcode lagi, supaya tetap akurat kalau
      // kategori/level mitigasi di database berubah di kemudian hari.
      const cellB = getCellInfoByScore(posB.value.score);
      const safeLevels = ['Low', 'Low-Medium'];
      isTargetAchieved.value = cellB ? safeLevels.includes(cellB.mitigation_level) : false;
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

    // Layout & kategori resmi matriks SELALU diambil dari database, bukan hardcode
    const matRes = await api.get('/matriks/mapping');
    if (matRes.data?.data && Array.isArray(matRes.data.data)) {
      matrixData.value = matRes.data.data;
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