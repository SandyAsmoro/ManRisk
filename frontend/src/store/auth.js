// ...\ManRiskMSKI\frontend\src\store\auth.js

import { defineStore } from 'pinia';
import api from '../utils/api';

export const useAuthStore = defineStore('auth', {
  state: () => {
    let storedUser = null;
    try {
      const rawUser = localStorage.getItem('user_data');
      if (rawUser && rawUser !== 'undefined') {
        storedUser = JSON.parse(rawUser);
      }
    } catch (e) {
      console.error("Gagal membaca data user dari storage", e);
      storedUser = null;
    }

    return {
      user: storedUser,
      token: localStorage.getItem('jwt_token') || null,
    };
  },
  
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  
  actions: {
    async login(username, password) {
      try {
        const response = await api.post('/auth/login', { username, password });
        
        // 🚨 PERBAIKAN: Menyesuaikan cara membaca struktur JSON dari backend
        const payload = response.data.data || response.data;
        
        this.token = payload.access_token || payload.token;
        this.user = payload.user;
        
        localStorage.setItem('jwt_token', this.token);
        localStorage.setItem('user_data', JSON.stringify(this.user));
        
        // Kembalikan data user agar router bisa membaca status must_change_password
        return this.user; 
      } catch (error) {
        throw error;
      }
    },

    async logout() {
      try {
        await api.post('/auth/logout');
      } catch (e) {
        console.error("Gagal memanggil API logout:", e);
      } finally {
        this.token = null;
        this.user = null;
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('user_data');
        window.location.href = '/login';
      }
    }
  }
});