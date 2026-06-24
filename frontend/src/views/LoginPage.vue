<!-- ...\ManRiskMSKI\frontend\src\views\LoginPage.vue -->

<template>
  <div class="flex items-center justify-center min-h-screen p-4 bg-gray-100">
    <div class="w-full max-w-md p-8 bg-white shadow-lg rounded-2xl">

      <!-- Header -->
      <div class="mb-8 text-center">
        <h1 class="text-2xl font-bold text-gray-800">ManRisk KPPN Malang</h1>
        <p class="mt-1 text-sm text-gray-500">Sistem Manajemen Risiko Operasional</p>
      </div>

      <!-- Error Banner -->
      <div
        v-if="errorMessage"
        class="flex items-start gap-3 p-4 mb-5 text-sm text-red-700 border border-red-200 rounded-lg bg-red-50"
        role="alert"
      >
        <svg class="w-5 h-5 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10A8 8 0 1 1 2 10a8 8 0 0 1 16 0zm-7-4a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM9 9a1 1 0 0 0 0 2v3a1 1 0 0 0 2 0v-3a1 1 0 0 0-1-1H9z" clip-rule="evenodd"/>
        </svg>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" novalidate>

        <!-- Username -->
        <div class="mb-4">
          <label for="username" class="block mb-1 text-sm font-medium text-gray-700">
            Username
          </label>
          <input
            id="username"
            v-model.trim="username"
            type="text"
            autocomplete="username"
            placeholder="Masukkan username"
            :disabled="isLoading"
            :class="[
              'w-full px-4 py-2.5 border rounded-lg text-sm transition focus:outline-none focus:ring-2',
              fieldError.username
                ? 'border-red-400 focus:ring-red-300'
                : 'border-gray-300 focus:ring-blue-300 focus:border-blue-400'
            ]"
            @input="clearFieldError('username')"
          />
          <p v-if="fieldError.username" class="mt-1 text-xs text-red-600">
            {{ fieldError.username }}
          </p>
        </div>

        <!-- Password -->
        <div class="mb-6">
          <label for="password" class="block mb-1 text-sm font-medium text-gray-700">
            Password
          </label>
          <div class="relative">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              placeholder="Masukkan password"
              :disabled="isLoading"
              :class="[
                'w-full px-4 py-2.5 pr-11 border rounded-lg text-sm transition focus:outline-none focus:ring-2',
                fieldError.password
                  ? 'border-red-400 focus:ring-red-300'
                  : 'border-gray-300 focus:ring-blue-300 focus:border-blue-400'
              ]"
              @input="clearFieldError('password')"
            />
            <!-- Toggle show/hide password -->
            <button
              type="button"
              tabindex="-1"
              class="absolute inset-y-0 flex items-center text-gray-400 right-3 hover:text-gray-600"
              @click="showPassword = !showPassword"
            >
              <!-- Eye icon (show) -->
              <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
              <!-- Eye-off icon (hide) -->
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M13.875 18.825A10.05 10.05 0 0 1 12 19c-4.477 0-8.268-2.943-9.542-7a9.97 9.97 0 0 1 2.425-3.94M6.53 6.53A9.97 9.97 0 0 1 12 5c4.477 0 8.268 2.943 9.542 7a9.97 9.97 0 0 1-4.423 5.348M3 3l18 18"/>
              </svg>
            </button>
          </div>
          <p v-if="fieldError.password" class="mt-1 text-xs text-red-600">
            {{ fieldError.password }}
          </p>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold rounded-lg text-sm transition focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-1 flex items-center justify-center gap-2"
        >
          <svg
            v-if="isLoading"
            class="w-4 h-4 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"/>
          </svg>
          {{ isLoading ? 'Memproses...' : 'Login' }}
        </button>

      </form>

      <p class="mt-6 text-xs text-center text-gray-400">
        Khusus pengguna internal KPPN Malang &bull; &copy; {{ new Date().getFullYear() }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';

const router    = useRouter();
const authStore = useAuthStore();

// ── State ────────────────────────────────────────────────────────────────────
const username     = ref('');
const password     = ref('');
const isLoading    = ref(false);
const showPassword = ref(false);
const errorMessage = ref('');
const fieldError   = reactive({ username: '', password: '' });

// ── Helpers ──────────────────────────────────────────────────────────────────
function clearFieldError(field) {
  fieldError[field] = '';
  errorMessage.value = '';
}

function validateForm() {
  let valid = true;
  if (!username.value) {
    fieldError.username = 'Username wajib diisi.';
    valid = false;
  }
  if (!password.value) {
    fieldError.password = 'Password wajib diisi.';
    valid = false;
  }
  return valid;
}

// ── Pesan error berdasarkan HTTP status ──────────────────────────────────────
function resolveErrorMessage(error) {
  // Tidak ada respons sama sekali → server mati / CORS / network
  if (!error.response) {
    return 'Tidak dapat terhubung ke server. Pastikan backend sudah berjalan dan coba lagi.';
  }

  const status  = error.response.status;
  const message = error.response.data?.message;

  switch (status) {
    case 400:
      return message || 'Data yang dikirim tidak valid. Periksa kembali username dan password.';
    case 401:
      return 'Username atau password salah. Silakan coba lagi.';
    case 403:
      return 'Akun Anda dinonaktifkan. Hubungi administrator KPPN.';
    case 404:
      // Route /api/auth/login belum ada di backend
      return 'Endpoint login tidak ditemukan (404). Hubungi administrator sistem.';
    case 429:
      return 'Terlalu banyak percobaan login. Tunggu beberapa menit lalu coba lagi.';
    case 500:
    case 502:
    case 503:
      return 'Terjadi kesalahan pada server. Coba beberapa saat lagi atau hubungi administrator.';
    default:
      return message || `Terjadi kesalahan (${status}). Silakan coba lagi.`;
  }
}

// ── Handler utama ─────────────────────────────────────────────────────────────
async function handleLogin() {
  errorMessage.value = '';
  fieldError.username = '';
  fieldError.password = '';

  if (!validateForm()) return;

  isLoading.value = true;
  try {
    await authStore.login(username.value, password.value);
    router.push('/');
  } catch (error) {
    errorMessage.value = resolveErrorMessage(error);
  } finally {
    isLoading.value = false;
  }
}
</script>