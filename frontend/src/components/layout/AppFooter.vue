<script setup>
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="bg-slate-900 text-white mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-10 pb-10 border-b border-white/10">

        <!-- Brand -->
        <div>
          <div class="flex items-center gap-3 mb-5">
            <div class="w-9 h-9 bg-[#0055A5] rounded-lg flex items-center justify-center flex-shrink-0">
              <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="white" stroke-width="2" stroke-linecap="round">
                <path d="M3 5 Q12 9 21 5"/>
                <line x1="7" y1="5" x2="7" y2="19"/>
                <line x1="17" y1="5" x2="17" y2="19"/>
                <path d="M3 19 Q12 15 21 19"/>
              </svg>
            </div>
            <div class="leading-none">
              <span class="block text-[15px] font-bold text-white tracking-tight">ARG<span class="text-[#009FDA]">Parts</span></span>
              <span class="block text-[10px] text-white/30 font-medium tracking-widest uppercase">Repuestos Japoneses</span>
            </div>
          </div>
          <p class="text-white/40 text-sm leading-relaxed max-w-xs">
            Especialistas en repuestos originales y alternativos para autos japoneses. Cotizamos por ti al mejor precio.
          </p>
        </div>

        <!-- Links -->
        <div>
          <h4 class="text-white/50 text-[11px] font-semibold uppercase tracking-widest mb-4">Navegación</h4>
          <ul class="space-y-2.5">
            <li><router-link to="/" class="text-white/50 hover:text-white text-sm transition-colors">Inicio</router-link></li>
            <li><router-link to="/catalogo" class="text-white/50 hover:text-white text-sm transition-colors">Catálogo de Repuestos</router-link></li>
            <li><router-link to="/cotizar" class="text-white/50 hover:text-white text-sm transition-colors">Solicitar Cotización</router-link></li>
          </ul>
        </div>

        <!-- Contact -->
        <div>
          <h4 class="text-white/50 text-[11px] font-semibold uppercase tracking-widest mb-4">Contacto</h4>
          <ul class="space-y-3">
            <li class="flex items-center gap-2.5 text-white/50 text-sm">
              <svg class="w-4 h-4 text-[#009FDA] flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              contacto@argparts.cl
            </li>
            <li class="flex items-center gap-2.5 text-white/50 text-sm">
              <svg class="w-4 h-4 text-[#009FDA] flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
              +56 9 XXXX XXXX
            </li>
            <li class="flex items-center gap-2.5 text-white/50 text-sm">
              <svg class="w-4 h-4 text-[#009FDA] flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              Santiago, Chile
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-8 flex flex-col sm:flex-row items-center justify-between gap-3">
        <p class="text-white/25 text-xs">© {{ currentYear }} ARGParts. Todos los derechos reservados.</p>
        <div class="flex items-center gap-4">
          <p class="text-white/20 text-xs">Desarrollado en Chile</p>
          <router-link
            to="/admin/login"
            class="text-white/15 hover:text-white/40 text-xs transition-colors"
          >Admin</router-link>
        </div>
      </div>
    </div>
  </footer>
</template>
