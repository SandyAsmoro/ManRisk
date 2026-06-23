<!-- ...\ManRiskMSKI\frontend\src\views\AdminPage.vue -->

<template>
  <div class="p-6 mx-auto max-w-7xl">

    <div class="flex flex-col items-start justify-between gap-4 mb-6 sm:flex-row sm:items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">Kelola User</h2>
        <p class="mt-1 text-sm text-gray-500">Kelola akun, hak akses, dan reset sandi pegawai.</p>
      </div>
      <router-link to="/register" class="px-4 py-2 text-white transition bg-blue-600 rounded shadow hover:bg-blue-700">
        + Tambah User Baru
      </router-link>
    </div>

    <div class="overflow-hidden bg-white border border-gray-100 shadow-sm rounded-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left border-collapse">
          <thead class="text-gray-600 border-b bg-gray-50">
            <tr>
              <th class="p-4 font-semibold">Nama & Username</th>
              <th class="p-4 font-semibold text-center">Seksi</th>
              <th class="p-4 font-semibold text-center">Role</th>
              <th class="p-4 font-semibold text-center">Aksi Lanjutan</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="u in users" :key="u.id" class="transition hover:bg-gray-50">
              <td class="p-4">
                <p class="font-bold text-gray-800">{{ u.full_name || '-' }}</p>
                <p class="text-xs text-gray-500">@{{ u.username }}</p>
              </td>
              <td class="p-4 text-center">
                <span class="px-2 py-1 text-xs font-semibold text-blue-700 rounded bg-blue-50">{{ u.section || '-' }}</span>
              </td>
              <td class="p-4 text-center">
                <span :class="u.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700'" class="px-2 py-1 text-xs font-bold uppercase rounded">{{ u.role }}</span>
              </td>
              <td class="p-4 text-center">
                <button @click="confirmReset(u)" class="px-3 py-1 text-xs font-bold text-orange-600 border border-orange-200 rounded bg-orange-50 hover:bg-orange-100">
                  Reset Password
                </button>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="4" class="p-8 text-center text-gray-500">Memuat data pengguna...</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm">
      <div class="w-full max-w-sm p-6 bg-white shadow-2xl rounded-2xl">
        <h3 class="mb-4 text-lg font-bold text-gray-800">Password Sementara</h3>
        <p class="mb-4 text-sm text-gray-600">Password untuk pengguna <strong>{{ selectedUser?.username }}</strong> telah direset menjadi:</p>
        <div class="p-3 mb-6 font-mono text-xl font-bold tracking-widest text-center text-blue-800 bg-blue-100 rounded-lg">
          {{ temporaryPassword }}
        </div>
        <p class="mb-6 text-xs text-red-600">Catat dan berikan password ini kepada pegawai bersangkutan. Mereka akan dipaksa mengganti password saat login.</p>
        <button @click="closeModal" class="w-full py-2 text-sm font-bold text-white transition bg-gray-800 rounded-lg hover:bg-gray-900">Tutup</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api';

const users = ref([]);

const showModal = ref(false);
const selectedUser = ref(null);
const temporaryPassword = ref('');

const fetchUsers = async () => {
  try {
    const res = await api.get('/auth/users');
    users.value = res.data.data;
  } catch (error) {
    console.error("Gagal mengambil data user:", error);
  }
};

const confirmReset = async (user) => {
  if (confirm(`Apakah Anda yakin ingin mereset password milik ${user.username}?`)) {
    try {
      const res = await api.post(`/auth/users/${user.id}/reset-password`);
      selectedUser.value = user;
      temporaryPassword.value = res.data.temporary_password;
      showModal.value = true;
    } catch (e) {
      alert(e.response?.data?.message || "Gagal mereset password.");
    }
  }
};

const closeModal = () => {
  showModal.value = false;
  selectedUser.value = null;
  temporaryPassword.value = '';
  fetchUsers();
};

onMounted(() => {
  fetchUsers();
});
</script>