<!-- ...\ManRiskMSKI\frontend\src\views\ChangePasswordPage.vue -->

<template>
  <div class="flex items-center justify-center min-h-screen px-4 py-12 bg-gray-50">
    <div class="w-full max-w-md p-8 bg-white border border-gray-100 shadow-lg rounded-xl">
      
      <div class="mb-8 text-center">
        <div class="inline-flex items-center justify-center w-12 h-12 mb-4 bg-red-100 rounded-full">
          <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-900">Perbarui Password Anda</h2>
        <p class="p-2 mt-2 text-sm font-medium text-red-600 rounded bg-red-50">
          Sistem mendeteksi bahwa password Anda telah direset. Anda wajib menggantinya sebelum melanjutkan.
        </p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label class="block mb-1 text-sm font-medium text-gray-700">Password Sementara (Dari Admin)</label>
          <input type="password" v-model="form.old_password" required 
                 class="w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
                 placeholder="Masukkan password saat ini" />
        </div>
        
        <div>
          <label class="block mb-1 text-sm font-medium text-gray-700">Password Baru</label>
          <input type="password" v-model="form.new_password" required minlength="6" 
                 class="w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
                 placeholder="Minimal 6 karakter" />
        </div>
        
        <div>
          <label class="block mb-1 text-sm font-medium text-gray-700">Konfirmasi Password Baru</label>
          <input type="password" v-model="form.confirm_password" required 
                 class="w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
                 placeholder="Ketik ulang password baru" />
        </div>

        <button type="submit" :disabled="loading" 
                class="w-full bg-blue-600 text-white py-2.5 rounded-lg font-semibold hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 transition disabled:opacity-70 flex justify-center items-center">
          <span v-if="loading">Menyimpan...</span>
          <span v-else>Simpan & Lanjutkan Masuk</span>
        </button>
      </form>
      
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
import api from '@/utils/api';

const authStore = useAuthStore();
const router = useRouter();
const loading = ref(false);

const form = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
});

const handleSubmit = async () => {
  if (form.value.new_password !== form.value.confirm_password) {
    return alert("Password baru dan konfirmasinya tidak cocok!");
  }

  loading.value = true;
  try {
    const response = await api.put('/auth/change-password', form.value);
    
    // Perbarui state global agar router berhenti memblokir halaman
    authStore.user.must_change_password = false;
    localStorage.setItem('user_data', JSON.stringify(authStore.user));
    
    alert(response.data.message || "Password berhasil diperbarui!");
    
    // Alihkan user ke halaman utama Dashboard
    router.push('/');
  } catch (error) {
    alert(error.response?.data?.message || "Gagal mengganti password.");
  } finally {
    loading.value = false;
  }
};
</script>