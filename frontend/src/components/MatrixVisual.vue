<template>
  <div class="w-full p-6 mx-auto font-sans bg-white">
    
    <div class="flex flex-col items-start justify-between gap-3 pb-4 mb-6 border-b sm:flex-row sm:items-center border-gray-50">
      <div>
        <h3 class="text-xl font-bold text-gray-800">Peta Matriks Heatmap Risiko</h3>
        <p class="text-xs text-gray-500 mt-0.5">Visualisasi dinamis berdasarkan data pemetaan sistem.</p>
      </div>
      <button 
        @click="toggleHighContrast" 
        class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold border rounded-lg transition-all shadow-sm shrink-0"
        :class="isHighContrast ? 'bg-gray-900 text-white border-gray-900' : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'"
        :aria-pressed="isHighContrast"
      >
        <span>👁️</span> {{ isHighContrast ? 'Mode Normal' : 'Kontras Tinggi' }}
      </button>
    </div>

    <div v-if="isLoading" class="flex items-center justify-center w-full py-20 text-gray-400">
      <span class="text-sm font-bold animate-pulse">Memuat data matriks...</span>
    </div>

    <div v-else class="flex flex-col items-center justify-center w-full gap-10 lg:flex-row lg:items-start" :class="{ 'high-contrast-mode': isHighContrast }">
      
      <div class="relative flex items-stretch mt-2 select-none">
        
        <div class="relative flex items-center justify-center w-12 mr-2">
          <div class="absolute text-[11px] font-bold text-gray-400 tracking-widest uppercase -rotate-90 whitespace-nowrap">
            Frekuensi
          </div>
          <div class="flex flex-col justify-between w-full h-full py-2 pr-2 text-xs font-bold text-right text-gray-500">
            <span v-for="y in reversedYAxis" :key="'y-label-'+y" class="flex items-center justify-end h-12">{{ y }}</span>
          </div>
        </div>

        <div class="flex flex-col">
          <div class="grid grid-cols-5 gap-1.5 bg-gray-50 p-2 rounded-xl border border-gray-200 shadow-inner w-fit" role="grid" aria-label="Matriks Risiko 5x5">
            <template v-for="freq in reversedYAxis" :key="'row-'+freq">
              <div 
                v-for="impact in xAxis" 
                :key="'cell-'+freq+'-'+impact"
                role="gridcell"
                class="relative flex flex-col items-center justify-center w-12 h-12 font-mono transition-all transform rounded-lg shadow-sm sm:w-14 sm:h-14 hover:scale-105 group"
                :class="getHighContrastClass(freq, impact)"
                :style="!isHighContrast ? getDynamicStyle(freq, impact) : {}"
                :aria-label="getAriaLabel(freq, impact)"
                tabindex="0"
              >
                <span class="z-10 text-base font-extrabold tracking-tight" :class="getTextColor(freq, impact)">
                  {{ getCellData(freq, impact).risk_value }}
                </span>
                <span class="absolute bottom-0.5 right-1 text-[9px] opacity-60" :class="getTextColor(freq, impact)" aria-hidden="true">
                  {{ getCellData(freq, impact).symbol }}
                </span>

                <div class="absolute hidden group-hover:block group-focus:block bottom-full mb-2 w-max bg-gray-900 text-white text-[10px] p-2 rounded-md shadow-md z-30 pointer-events-none text-center leading-normal">
                  Koordinat F:{{ freq }} , D:{{ impact }}<br>
                  <span class="font-bold" :style="{ color: getCellData(freq, impact).color_code }">
                    Skor: {{ getCellData(freq, impact).risk_value }} ({{ getCellData(freq, impact).category }})
                  </span>
                </div>
              </div>
            </template>
          </div>

          <div class="grid grid-cols-5 gap-1.5 px-1.5 mt-1.5 w-full text-center text-xs font-bold text-gray-500">
            <span v-for="x in xAxis" :key="'x-label-'+x" class="inline-block w-12 sm:w-14">{{ x }}</span>
          </div>
          <div class="text-center mt-2 text-[11px] font-bold text-gray-400 tracking-widest uppercase">
            Dampak
          </div>
        </div>
      </div>

      <div class="flex flex-col justify-start w-full pt-6 border-t border-gray-100 lg:w-64 lg:border-t-0 lg:border-l lg:pt-0 lg:pl-8">
        <h4 class="mb-4 text-xs font-bold tracking-wider text-gray-500 uppercase" id="legend-title">
          Klarifikasi Tingkat Risiko
        </h4>
        <div class="flex flex-col gap-3 text-xs" aria-labelledby="legend-title">
          <div v-for="cat in uniqueCategories" :key="cat.category" class="flex items-center gap-3 bg-gray-50 p-2.5 rounded-xl border border-gray-100 shadow-sm transition-all hover:bg-gray-100">
            <span 
              class="flex items-center justify-center w-6 h-6 text-xs font-extrabold rounded-lg shadow-sm shrink-0"
              :class="isHighContrast ? 'bg-white text-black border border-gray-400' : ''"
              :style="!isHighContrast ? { backgroundColor: cat.color_code, color: getContrastYIQ(cat.color_code) } : {}"
              aria-hidden="true"
            >
              {{ cat.symbol }}
            </span>
            <div class="flex flex-col">
              <span class="font-bold leading-tight text-gray-800">{{ cat.description }}</span>
              <span class="text-[10px] text-gray-500 font-semibold mt-0.5">Kategori {{ cat.category }} ({{ cat.mitigation_level }})</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/utils/api';

const xAxis = [1, 2, 3, 4, 5];
const reversedYAxis = [5, 4, 3, 2, 1];
const isHighContrast = ref(false);
const isLoading = ref(true);
const matrixData = ref([]);

const toggleHighContrast = () => {
  isHighContrast.value = !isHighContrast.value;
};

// 🚨 PERBAIKAN: sebelumnya pakai fetch() langsung ke path relatif '/api/matriks/mapping'
// (yang di Netlify tidak mengarah ke backend Vercel -> selalu gagal/CORS) dan token
// 'access_token' yang TIDAK PERNAH disimpan di mana pun (komponen lain menyimpan
// 'jwt_token', lihat utils/api.js). Akibatnya request selalu gagal diam-diam dan
// matriks selalu jatuh ke fallback N/A. Sekarang pakai instance axios `api` yang sama
// dengan komponen lain agar baseURL & Bearer token selalu konsisten dan data SELALU
// mengikuti isi tabel risk_matrix_mapping di database.
const fetchMatrixData = async () => {
  try {
    isLoading.value = true;
    const response = await api.get('/matriks/mapping');
    if (response.data && response.data.status === 'success') {
      matrixData.value = response.data.data;
    }
  } catch (error) {
    console.error('Gagal memuat data mapping matriks:', error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchMatrixData();
});

// Helper Function: Cek hex butuh teks hitam atau putih (YIQ Ratio)
const getContrastYIQ = (hexcolor) => {
  if(!hexcolor) return 'black';
  hexcolor = hexcolor.replace("#", "");
  const r = parseInt(hexcolor.substr(0,2),16);
  const g = parseInt(hexcolor.substr(2,2),16);
  const b = parseInt(hexcolor.substr(4,2),16);
  const yiq = ((r*299)+(g*587)+(b*114))/1000;
  return (yiq >= 128) ? 'black' : 'white';
};

const getCellData = (freq, impact) => {
  const cell = matrixData.value.find(item => item.frequency === freq && item.impact === impact);
  if (!cell) {
    return { risk_value: 0, category: 'N/A', color_code: '#E5E7EB', description: '-', symbol: '-' }; // Fallback jika DB kosong
  }
  
  // Tentukan simbol secara dinamis berdasarkan hex/nama
  let symbol = '●';
  if(cell.category.toLowerCase().includes('hijau')) symbol = '▲';
  if(cell.category.toLowerCase().includes('kuning')) symbol = '■';
  if(cell.category.toLowerCase().includes('oranye')) symbol = '◆';
  if(cell.category.toLowerCase().includes('merah')) symbol = '★';

  return { ...cell, symbol };
};

const getTextColor = (freq, impact) => {
  if (isHighContrast.value) return ''; 
  const cell = getCellData(freq, impact);
  return getContrastYIQ(cell.color_code) === 'white' ? 'text-white' : 'text-gray-900';
};

const getDynamicStyle = (freq, impact) => {
  const cell = getCellData(freq, impact);
  return { backgroundColor: cell.color_code };
};

const getHighContrastClass = (freq, impact) => {
  if (!isHighContrast.value) return '';
  const cat = getCellData(freq, impact).category.toLowerCase();
  if (cat.includes('merah')) return 'bg-black text-white border border-white ring-1 ring-black';
  if (cat.includes('oranye')) return 'bg-gray-700 text-white border border-white';
  if (cat.includes('kuning')) return 'bg-gray-400 text-black border border-gray-900';
  if (cat.includes('hijau')) return 'bg-gray-200 text-black border border-gray-600';
  return 'bg-white text-black border border-black';
};

const getAriaLabel = (freq, impact) => {
  const cell = getCellData(freq, impact);
  return `Frekuensi ${freq}, Dampak ${impact}, Skor ${cell.risk_value}, Klasifikasi ${cell.description} Kategori ${cell.category}`;
};

// Ekstrak Legend Kategori Unik dari Data Matrix
const uniqueCategories = computed(() => {
  const uniqueMap = new Map();
  matrixData.value.forEach(item => {
    let symbol = '●';
    const catLower = item.category.toLowerCase();
    if (catLower.includes('hijau')) symbol = '▲';
    if (catLower.includes('kuning')) symbol = '■';
    if (catLower.includes('oranye') || catLower.includes('jingga')) symbol = '◆';
    if (catLower.includes('merah')) symbol = '★';

    const existing = uniqueMap.get(item.category);
    // Simpan baris dengan risk_value PALING RENDAH per kategori, supaya urutan legend
    // selalu konsisten & benar tanpa bergantung urutan baris yang dikembalikan database.
    if (!existing || item.risk_value < existing.risk_value) {
      uniqueMap.set(item.category, { ...item, symbol });
    }
  });

  // Urutkan legend dari risiko terendah ke tertinggi
  return Array.from(uniqueMap.values()).sort((a, b) => a.risk_value - b.risk_value);
});
</script>

<style scoped>
div[role="gridcell"] {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
div[role="gridcell"]:focus {
  outline: 3px solid #2563eb;
  outline-offset: 1px;
  z-index: 20;
}
</style>