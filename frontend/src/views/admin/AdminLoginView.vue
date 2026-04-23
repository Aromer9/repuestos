<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center px-4">
    <div class="w-full max-w-md">

      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center gap-2.5 mb-2">
          <div class="w-9 h-9 bg-[#003087] rounded-lg flex items-center justify-center">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="white" stroke-width="2" stroke-linecap="round">
              <path d="M3 5 Q12 9 21 5"/>
              <line x1="7" y1="5" x2="7" y2="19"/>
              <line x1="17" y1="5" x2="17" y2="19"/>
              <path d="M3 19 Q12 15 21 19"/>
            </svg>
          </div>
          <span class="text-xl font-bold text-slate-900 tracking-tight">ARGParts</span>
        </div>
        <p class="text-slate-500 text-sm">Panel de administración</p>
      </div>

      <!-- Card -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
        <h1 class="text-xl font-semibold text-slate-900 mb-1">Iniciar sesión</h1>
        <p class="text-slate-500 text-sm mb-6">Acceso restringido al equipo ARGParts</p>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Usuario</label>
            <input
              v-model="username"
              type="text"
              autocomplete="username"
              placeholder="tu usuario"
              class="w-full px-4 py-2.5 rounded-lg border border-slate-300 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-[#0055A5] focus:border-transparent placeholder:text-slate-400 transition"
              :class="{ 'border-red-400': error }"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Contraseña</label>
            <div class="relative">
              <input
                v-model="password"
                :type="showPass ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="••••••••"
                class="w-full px-4 py-2.5 rounded-lg border border-slate-300 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-[#0055A5] focus:border-transparent placeholder:text-slate-400 transition pr-10"
                :class="{ 'border-red-400': error }"
              />
              <button
                type="button"
                @click="showPass = !showPass"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <svg v-if="!showPass" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Error -->
          <div v-if="error" class="flex items-center gap-2 text-red-600 text-sm bg-red-50 rounded-lg px-3 py-2.5 border border-red-200">
            <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading || !username || !password"
            class="w-full py-2.5 rounded-lg text-white text-sm font-semibold transition"
            style="background-color: #003087;"
            :class="{ 'opacity-60 cursor-not-allowed': loading || !username || !password }"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Ingresando...
            </span>
            <span v-else>Ingresar al panel</span>
          </button>
        </form>
      </div>

      <p class="text-center text-xs text-slate-400 mt-6">
        <a href="/" class="hover:text-slate-600 transition">← Volver al sitio</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { login, loading, error } = useAuth()

const username = ref('')
const password = ref('')
const showPass = ref(false)

const handleLogin = async () => {
  const ok = await login(username.value, password.value)
  if (ok) router.push({ name: 'admin' })
}
</script>
