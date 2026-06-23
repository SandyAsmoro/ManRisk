<!-- ...\ManRiskMSKI\frontend\src\components\MatrixVisual.vue -->

<template>
  <div class="w-full p-6 mx-auto font-sans bg-white">
    
    <div class="flex flex-col items-start justify-between gap-3 pb-4 mb-6 border-b sm:flex-row sm:items-center border-gray-50">
      <div>
        <h3 class="text-xl font-bold text-gray-800">Peta Matriks Heatmap Risiko Kemenkeu</h3>
        <p class="text-xs text-gray-500 mt-0.5">Visualisasi hubungan tingkat Frekuensi (Sumbu Y) dan Dampak (Sumbu X).</p>
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

    <div class="flex flex-col items-center justify-center w-full gap-10 lg:flex-row lg:items-start" :class="{ 'high-contrast-mode': isHighContrast }">
      
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
                :class="getCellClass(freq, impact)"
                :aria-label="getAriaLabel(freq, impact)"
                tabindex="0"
              >
                <span class="z-10 text-base font-extrabold tracking-tight">{{ getOfficialValue(freq, impact) }}</span>
                <span class="absolute bottom-0.5 right-1 text-[9px] opacity-45" aria-hidden="true">
                  {{ getCategory(freq, impact).symbol }}
                </span>

                <div class="absolute hidden group-hover:block group-focus:block bottom-full mb-2 w-max bg-gray-900 text-white text-[10px] p-2 rounded-md shadow-md z-30 pointer-events-none text-center leading-normal">
                  Koordinat F:{{ freq }} , D:{{ impact }}<br>
                  <span class="font-bold text-yellow-400">Skor Kemenkeu: {{ getOfficialValue(freq, impact) }} ({{ getCategory(freq, impact).labelColor }})</span>
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
          <div v-for="cat in uniqueCategories" :key="cat.name" class="flex items-center gap-3 bg-gray-50 p-2.5 rounded-xl border border-gray-100 shadow-sm transition-all hover:bg-gray-100">
            <span 
              class="flex items-center justify-center w-6 h-6 text-xs font-extrabold rounded-lg shadow-sm shrink-0"
              :class="cat.colorClass + (isHighContrast ? ' border border-gray-400' : '')"
              aria-hidden="true"
            >
              {{ cat.symbol }}
            </span>
            <div class="flex flex-col">
              <span class="font-bold leading-tight text-gray-800">{{ cat.name }}</span>
              <span class="text-[10px] text-gray-500 font-semibold mt-0.5">Kategori {{ cat.labelColor }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const xAxis = [1, 2, 3, 4, 5];
const reversedYAxis = [5, 4, 3, 2, 1];
const isHighContrast = ref(false);

const toggleHighContrast = () => {
  isHighContrast.value = !isHighContrast.value;
};

const officialMatrixLayout = {
  5: { 1: 9, 2: 15, 3: 18, 4: 23, 5: 25 },
  4: { 1: 6, 2: 12, 3: 16, 4: 19, 5: 24 },
  3: { 1: 4, 2: 10, 3: 14, 4: 17, 5: 22 },
  2: { 1: 2, 2: 7,  3: 11, 4: 13, 5: 21 },
  1: { 1: 1, 2: 3,  3: 5,  4: 8,  5: 20 }
};

const getOfficialValue = (freq, impact) => officialMatrixLayout[freq]?.[impact] || 0;

const getCategory = (freq, impact) => {
  const score = getOfficialValue(freq, impact);
  if (score <= 5)   return { name: 'Risiko Rendah', labelColor: 'Biru', colorClass: 'bg-blue-500 text-white', symbol: '●' };
  if (score <= 11)  return { name: 'Risiko Sedang Rendah', labelColor: 'Hijau', colorClass: 'bg-green-500 text-white', symbol: '▲' };
  if (score <= 15)  return { name: 'Risiko Sedang', labelColor: 'Kuning', colorClass: 'bg-yellow-400 text-yellow-950', symbol: '■' };
  if (score <= 19)  return { name: 'Risiko Tinggi', labelColor: 'Jingga', colorClass: 'bg-orange-500 text-white', symbol: '◆' };
  return { name: 'Risiko Sangat Tinggi', labelColor: 'Merah', colorClass: 'bg-red-600 text-white', symbol: '★' };
};

const uniqueCategories = computed(() => {
  return [
    { name: 'Risiko Rendah', labelColor: 'Biru', colorClass: 'bg-blue-500 text-white', symbol: '●' },
    { name: 'Risiko Sedang Rendah', labelColor: 'Hijau', colorClass: 'bg-green-500 text-white', symbol: '▲' },
    { name: 'Risiko Sedang', labelColor: 'Kuning', colorClass: 'bg-yellow-400 text-yellow-950', symbol: '■' },
    { name: 'Risiko Tinggi', labelColor: 'Jingga', colorClass: 'bg-orange-500 text-white', symbol: '◆' },
    { name: 'Risiko Sangat Tinggi', labelColor: 'Merah', colorClass: 'bg-red-600 text-white', symbol: '★' },
  ];
});

const getCellClass = (freq, impact) => {
  const cat = getCategory(freq, impact);
  if (isHighContrast.value) {
    if (cat.labelColor === 'Merah') return 'bg-black text-white border border-white ring-1 ring-black';
    if (cat.labelColor === 'Jingga') return 'bg-gray-700 text-white border border-white';
    if (cat.labelColor === 'Kuning') return 'bg-gray-400 text-black border border-gray-900';
    if (cat.labelColor === 'Hijau') return 'bg-gray-200 text-black border border-gray-600';
    return 'bg-white text-black border border-black';
  }
  return cat.colorClass;
};

const getAriaLabel = (freq, impact) => {
  const cat = getCategory(freq, impact);
  const score = getOfficialValue(freq, impact);
  return `Frekuensi ${freq}, Dampak ${impact}, Skor Kemenkeu ${score}, Klasifikasi ${cat.name} Kategori ${cat.labelColor}`;
};
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