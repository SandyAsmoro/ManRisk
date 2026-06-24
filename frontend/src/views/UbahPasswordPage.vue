<template>
  <div class="p-6">
    <div class="max-w-xl p-8 mx-auto bg-white border border-gray-100 shadow-md rounded-xl">
      <div class="mb-6">
        <h2 class="text-2xl font-bold text-gray-900">Ubah Password Akun</h2>
        <p class="mt-1 text-sm text-gray-500">
          Perbarui password Anda secara berkala untuk menjaga keamanan akun.
        </p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label class="block mb-1 text-sm font-medium text-gray-700">Password Lama</label>
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
          <span v-if="loading">Menyimpan Perubahan...</span>
          <span v-else>Simpan Password Baru</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/utils/api';

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
    alert(response.data.message || "Password berhasil diperbarui!");
    
    // Kosongkan form setelah berhasil
    form.value = {
      old_password: '',
      new_password: '',
      confirm_password: ''
    };
  } catch (error) {
    alert(error.response?.data?.message || "Gagal mengganti password. Pastikan password lama benar.");
  } finally {
    loading.value = false;
  }
};
</script>