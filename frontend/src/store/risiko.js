// ...\ManRiskMSKI\frontend\src\store\risiko.js

import { defineStore } from 'pinia';
import api from '@/utils/api';

export const useRisikoStore = defineStore('risiko', {
  state: () => ({
    indicators: [],
    isLoading: false,
    error: null
  }),
  actions: {
    async fetchIndicators() {
      this.isLoading = true;
      try {
        const response = await api.get('/risiko/indicators');
        this.indicators = response.data.data;
      } catch (err) {
        this.error = 'Gagal memuat indikator';
      } finally {
        this.isLoading = false;
      }
    },
    async saveAssessment(payload) {
      this.isLoading = true;
      try {
        await api.post('/risiko/assessment', payload);
        return { success: true };
      } catch (err) {
        return { success: false, message: err.response?.data?.message || 'Gagal menyimpan' };
      } finally {
        this.isLoading = false;
      }
    }
  }
});