<!-- ...\ManRiskMSKI\frontend\src\views\RegisterPage.vue -->

<template>
  <div class="max-w-3xl p-6 mx-auto bg-white rounded-lg shadow">
    <div class="pb-4 mb-6 border-b border-gray-200">
      <h2 class="text-2xl font-bold text-gray-800">Manajemen Pengguna</h2>
      <p class="mt-1 text-sm text-gray-500">Tambah akun pengguna baru untuk akses Sistem Manajemen Risiko.</p>
    </div>

    <div v-if="successMessage" class="p-4 mb-6 text-sm text-green-700 bg-green-100 border border-green-200 rounded-lg">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
        <span class="font-medium">{{ successMessage }}</span>
      </div>
    </div>

    <div v-if="errorMessage" class="p-4 mb-6 text-sm text-red-700 bg-red-100 border border-red-200 rounded-lg">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        <span class="font-medium">{{ errorMessage }}</span>
      </div>
    </div>

    <form @submit.prevent="handleRegister" class="space-y-5">
      
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <div>
          <label class="block mb-1 text-sm font-medium text-gray-700">Username <span class="text-red-500">*</span></label>
          <input type="text" v-model="form.username" required placeholder="Contoh: andi_budiman" 
                 class="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" />
        </div>
        <div>
          <label class="block mb-1 text-sm font-medium text-gray-700">Email <span class="text-red-500">*</span></label>
          <input type="email" v-model="form.email" required placeholder="Contoh: andi@kppn.local" 
                 class="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <div>
          <label class="block mb-1 text-sm font-medium text-gray-700">Password Sementara <span class="text-red-500">*</span></label>
          <input type="password" v-model="form.password" required placeholder="Minimal 6 karakter" minlength="6"
                 class="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" />
        </div>
        <div>
          <label class="block mb-1 text-sm font-medium text-gray-700">Nama Lengkap</label>
          <input type="text" v-model="form.full_name" placeholder="Contoh: Andi Budiman, S.E." 
                 class="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <div>
          <label class="block mb-1 text-sm font-medium text-gray-700">Hak Akses (Role)</label>
          <select v-model="form.role" class="w-full p-2.5 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none">
            <option value="user">User Biasa</option>
            <option value="admin">Administrator</option>
          </select>
        </div>
        <div>
          <label class="block mb-1 text-sm font-medium text-gray-700">Seksi / Unit Kerja</label>
          <select v-model="form.section" class="w-full p-2.5 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none">
            <option value="">-- Pilih Unit Kerja --</option>
            <option value="Subbagian Umum">Subbagian Umum</option>
            <option value="Seksi MSKI">Seksi MSKI</option>
            <option value="Seksi Bank">Seksi Bank</option>
            <option value="Seksi Vera">Seksi Vera</option>
            <option value="Seksi Pencairan Dana">Seksi Pencairan Dana</option>
          </select>
        </div>
      </div>

      <div class="pt-4 mt-6 border-t border-gray-100">
        <button type="submit" :disabled="isLoading" 
                class="w-full md:w-auto px-6 py-2.5 text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 font-medium transition disabled:opacity-60 flex justify-center items-center gap-2">
          <svg v-if="isLoading" class="w-5 h-5 text-white animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          {{ isLoading ? 'Memproses Data...' : 'Simpan Pengguna Baru' }}
        </button>
      </div>

    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/utils/api'; // Menggunakan Axios instance yang otomatis menyematkan token JWT

const form = ref({
  username: '',
  email: '',
  password: '',
  full_name: '',
  role: 'user',
  section: ''
});

const isLoading = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

const handleRegister = async () => {
  isLoading.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  try {
    // Tembak endpoint auth/register
    const response = await api.post('/auth/register', form.value);
    
    // Tampilkan notifikasi sukses dari backend
    successMessage.value = response.data.message || 'Pengguna berhasil didaftarkan!';
    
    // Reset form ke posisi awal (kosong)
    form.value = {
      username: '',
      email: '',
      password: '',
      full_name: '',
      role: 'user',
      section: ''
    };
    
    // Hilangkan pesan sukses setelah 5 detik
    setTimeout(() => { successMessage.value = ''; }, 5000);
    
  } catch (error) {
    // Tangkap error dari backend (misal: Username sudah dipakai, atau Email duplikat)
    errorMessage.value = error.response?.data?.message || 'Terjadi kesalahan jaringan saat menyimpan data.';
  } finally {
    isLoading.value = false;
  }
};
</script>