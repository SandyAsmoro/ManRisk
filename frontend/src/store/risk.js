// ...\ManRiskMSKI\frontend\src\store\risk.js

import { defineStore } from 'pinia';
import api from '../utils/api';

export const useRiskStore = defineStore('risk', {
  state: () => ({
    indicators: [],
  }),
  
  actions: {
    async fetchIndicators() {
      // Hanya ambil dari backend jika data indikator masih kosong
      if (this.indicators.length === 0) {
        try {
          const response = await api.get('/risiko/indicators');
          this.indicators = response.data.data;
        } catch (error) {
          console.error("Gagal mengambil data indikator risiko:", error);
        }
      }
    }
  }
});