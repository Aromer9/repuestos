<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const mobileMenuOpen = ref(false)
const scrolled = ref(false)

const navLinks = [
  { name: 'Inicio', to: '/' },
  { name: 'Catálogo', to: '/catalogo' },
  { name: 'Cotizar', to: '/cotizar' },
]

const handleScroll = () => { scrolled.value = window.scrollY > 10 }
onMounted(() => window.addEventListener('scroll', handleScroll))
onUnmounted(() => window.removeEventListener('scroll', handleScroll))
</script>

<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 bg-white"
    :class="scrolled ? 'shadow-sm border-b border-slate-200' : 'border-b border-slate-200'"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 md:h-[72px]">

        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-3 group">
          <div class="w-9 h-9 bg-[#003087] rounded-lg flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-105">
            <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="white" stroke-width="2" stroke-linecap="round">
              <!-- Géminis: dos pilares con arcos arriba y abajo -->
              <path d="M3 5 Q12 9 21 5"/>
              <line x1="7" y1="5" x2="7" y2="19"/>
              <line x1="17" y1="5" x2="17" y2="19"/>
              <path d="M3 19 Q12 15 21 19"/>
            </svg>
          </div>
          <div class="leading-none">
            <span class="block text-[15px] font-bold text-slate-900 tracking-tight">ARG<span class="text-[#0055A5]">Parts</span></span>
            <span class="block text-[10px] text-slate-400 font-medium tracking-widest uppercase">Repuestos Japoneses</span>
          </div>
        </router-link>

        <!-- Desktop Nav -->
        <nav class="hidden md:flex items-center gap-1">
          <router-link
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150"
            :class="route.path === link.to
              ? 'text-[#0055A5] bg-[#E8F2FB]'
              : 'text-slate-600 hover:text-[#0055A5] hover:bg-[#E8F2FB]'"
          >
            {{ link.name }}
          </router-link>
        </nav>

        <!-- CTA + Burger -->
        <div class="flex items-center gap-3">
          <router-link to="/cotizar" class="hidden md:inline-flex btn-primary text-sm px-5 py-2.5">
            Solicitar Cotización
          </router-link>
          <button
            class="md:hidden p-2 rounded-md hover:bg-slate-100 transition-colors"
            @click="mobileMenuOpen = !mobileMenuOpen"
            aria-label="Menú"
          >
            <svg class="w-5 h-5 text-slate-700" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
              <path v-else stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Menu -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div v-if="mobileMenuOpen" class="md:hidden bg-white border-b border-slate-200 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 py-3 flex flex-col gap-1">
          <router-link
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="px-4 py-3 rounded-md text-sm font-medium transition-colors"
            :class="route.path === link.to ? 'text-[#0055A5] bg-[#E8F2FB]' : 'text-slate-600 hover:text-[#0055A5] hover:bg-[#E8F2FB]'"
            @click="mobileMenuOpen = false"
          >
            {{ link.name }}
          </router-link>
          <router-link to="/cotizar" class="btn-primary mt-2 text-sm" @click="mobileMenuOpen = false">
            Solicitar Cotización
          </router-link>
        </div>
      </div>
    </transition>
  </header>
</template>
