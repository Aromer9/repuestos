<script setup>
const subaruModels = [
  { name: 'Forester', years: '1997–2024' },
  { name: 'Outback', years: '1994–2024' },
  { name: 'Impreza', years: '1992–2024' },
  { name: 'XV / Crosstrek', years: '2011–2024' },
  { name: 'Legacy', years: '1989–2024' },
  { name: 'BRZ / GR86', years: '2012–2024' },
]

const brands = [
  { name: 'Subaru', featured: true },
  { name: 'Toyota', featured: false },
  { name: 'Honda', featured: false },
  { name: 'Nissan', featured: false },
  { name: 'Mitsubishi', featured: false },
  { name: 'Mazda', featured: false },
  { name: 'Suzuki', featured: false },
  { name: 'Isuzu', featured: false },
]

const benefits = [
  {
    icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
    title: 'Verificación por VIN',
    description: 'Confirmamos el repuesto exacto para tu vehículo usando el número de chasis. Cero errores de compatibilidad.',
  },
  {
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
    title: 'Múltiples proveedores',
    description: 'Cotizamos con varios distribuidores simultáneamente y te entregamos siempre el mejor precio disponible.',
  },
  {
    icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z',
    title: 'Contacto inmediato',
    description: 'Un agente te escribe por WhatsApp en minutos. Cotización confirmada en menos de 24 horas.',
  },
]

const categories = [
  { name: 'Frenos',      icon: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4' },
  { name: 'Motor',       icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' },
  { name: 'Suspensión',  icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
  { name: 'Transmisión', icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15' },
  { name: 'Eléctrico',   icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
  { name: 'Filtros',     icon: 'M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z' },
]
</script>

<template>
  <div>

    <!-- ══════════════════════ HERO ══════════════════════ -->
    <section class="min-h-screen flex items-center justify-center bg-white">
      <div class="w-full max-w-3xl mx-auto px-6 py-32 text-center">

        <div class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#E8F2FB] border border-[#0055A5]/20 rounded-full mb-8">
          <svg viewBox="0 0 18 18" class="w-3.5 h-3.5" fill="none">
            <circle cx="6" cy="8.5" r="2.5" fill="#0055A5"/>
            <circle cx="12.5" cy="8" r="1.8" fill="#0055A5" opacity="0.75"/>
            <circle cx="9.5" cy="5" r="1.3" fill="#0055A5" opacity="0.65"/>
          </svg>
          <span class="text-[#0055A5] text-xs font-semibold tracking-widest uppercase">Especialistas en Subaru — Chile</span>
        </div>

        <h1 class="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-slate-900 leading-[1.05] tracking-tight mb-6">
          El repuesto exacto<br>para tu
          <span class="text-[#0055A5]"> Subaru</span>
        </h1>

        <p class="text-slate-500 text-lg leading-relaxed mb-10 max-w-xl mx-auto">
          Forester, Outback, Impreza, XV y más. Deja tus datos y un agente cotiza
          con múltiples proveedores para darte el mejor precio.
        </p>

        <div class="flex flex-col sm:flex-row gap-3 justify-center">
          <router-link to="/cotizar?marca=Subaru" class="btn-primary text-base px-8 py-4">
            Cotizar repuesto Subaru
            <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
            </svg>
          </router-link>
          <router-link to="/catalogo?marca=Subaru" class="btn-secondary text-base px-8 py-4">
            Ver catálogo
          </router-link>
        </div>

        <!-- Stats -->
        <div class="flex flex-wrap gap-12 mt-16 pt-10 border-t border-slate-200 justify-center">
          <div>
            <p class="text-3xl font-bold text-slate-900">8+</p>
            <p class="text-slate-400 text-sm mt-0.5">Marcas japonesas</p>
          </div>
          <div>
            <p class="text-3xl font-bold text-slate-900">500+</p>
            <p class="text-slate-400 text-sm mt-0.5">Repuestos disponibles</p>
          </div>
          <div>
            <p class="text-3xl font-bold text-slate-900">&lt;24h</p>
            <p class="text-slate-400 text-sm mt-0.5">Tiempo de respuesta</p>
          </div>
        </div>

      </div>
    </section>

    <!-- ══════════════════════ HOW IT WORKS ══════════════════════ -->
    <section class="py-20 bg-slate-50 border-y border-slate-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-14">
          <p class="text-[#0055A5] text-xs font-semibold uppercase tracking-widest mb-3">Proceso simple</p>
          <h2 class="section-title">¿Cómo funciona?</h2>
          <p class="section-subtitle max-w-md mx-auto">Tú nos das los datos, nosotros hacemos todo el trabajo.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          <div class="hidden md:block absolute top-8 left-[calc(33%+2rem)] right-[calc(33%+2rem)] h-px bg-surface-300"></div>

          <div v-for="(step, i) in [
            { n:'01', title:'Llena el formulario', desc:'Nombre, RUT, teléfono, marca, modelo, año y VIN de tu vehículo.' },
            { n:'02', title:'Cotizamos por ti', desc:'Nuestro agente consulta múltiples proveedores y obtiene el mejor precio.' },
            { n:'03', title:'Recibe tu cotización', desc:'Te escribimos por WhatsApp. Tú decides si procedes con la compra.' },
          ]" :key="i" class="text-center">
            <div class="w-16 h-16 mx-auto mb-5 rounded-full border-2 border-[#0055A5] bg-white flex items-center justify-center shadow-sm">
              <span class="text-[#0055A5] font-bold text-sm tracking-wider">{{ step.n }}</span>
            </div>
            <h3 class="text-slate-900 font-semibold text-lg mb-2">{{ step.title }}</h3>
            <p class="text-slate-500 text-sm leading-relaxed max-w-xs mx-auto">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════ BENEFITS ══════════════════════ -->
    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="section-title">Por qué elegirnos</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            v-for="benefit in benefits"
            :key="benefit.title"
            class="card p-8 group"
          >
            <div class="w-12 h-12 bg-[#E8F2FB] rounded-xl flex items-center justify-center mb-5 group-hover:bg-[#0055A5]/10 transition-colors">
              <svg class="w-6 h-6 text-[#0055A5]" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" :d="benefit.icon"/>
              </svg>
            </div>
            <h3 class="text-slate-900 font-semibold text-lg mb-2">{{ benefit.title }}</h3>
            <p class="text-slate-500 text-sm leading-relaxed">{{ benefit.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════ BRANDS ══════════════════════ -->
    <section class="py-16 bg-slate-50 border-y border-slate-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10">
          <div>
            <p class="text-slate-400 text-[11px] font-semibold uppercase tracking-widest mb-1">Cobertura completa</p>
            <h2 class="text-2xl font-bold text-slate-900">Marcas japonesas disponibles</h2>
          </div>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          <router-link
            v-for="brand in brands"
            :key="brand.name"
            :to="`/catalogo?marca=${brand.name}`"
            class="group flex flex-col items-center justify-center gap-1.5 py-4 px-3 rounded-lg border text-center transition-all duration-150 cursor-pointer"
            :class="brand.featured
              ? 'bg-[#0055A5] text-white border-[#0055A5] hover:bg-[#003087]'
              : 'bg-white text-slate-600 border-slate-200 hover:border-[#0055A5]/30 hover:text-[#0055A5] hover:bg-[#E8F2FB]'"
          >
            <span class="text-sm font-semibold">{{ brand.name }}</span>
            <span v-if="brand.featured" class="text-[10px] text-white/70 font-medium">Principal</span>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ══════════════════════ CATEGORIES ══════════════════════ -->
    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col sm:flex-row sm:items-end justify-between mb-10 gap-4">
          <div>
            <p class="text-[#0055A5] text-[11px] font-semibold uppercase tracking-widest mb-1">Catálogo</p>
            <h2 class="text-2xl font-bold text-slate-900">Categorías de repuestos</h2>
          </div>
          <router-link to="/catalogo" class="btn-secondary text-sm px-5 py-2.5 self-start sm:self-auto">
            Ver catálogo completo →
          </router-link>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <router-link
            v-for="cat in categories"
            :key="cat.name"
            :to="`/catalogo?categoria=${cat.name}`"
            class="group card p-5 flex flex-col items-center gap-3 text-center"
          >
            <div class="w-11 h-11 bg-[#E8F2FB] rounded-xl flex items-center justify-center group-hover:bg-[#0055A5]/10 transition-colors">
              <svg class="w-5 h-5 text-[#0055A5]" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" :d="cat.icon"/>
              </svg>
            </div>
            <span class="text-slate-600 group-hover:text-[#0055A5] text-sm font-medium transition-colors">{{ cat.name }}</span>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ══════════════════════ CTA FINAL ══════════════════════ -->
    <section class="py-20 bg-[#003087]">
      <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <p class="text-white/60 text-[11px] font-semibold uppercase tracking-widest mb-4">Cotización gratuita · Sin compromiso</p>
        <h2 class="text-4xl md:text-5xl font-extrabold text-white mb-5 leading-tight">
          ¿Necesitas un repuesto<br>para tu Subaru?
        </h2>
        <p class="text-white/60 text-lg mb-10">
          Déjanos tus datos y te cotizamos al instante con los mejores proveedores del mercado.
        </p>
        <router-link
          to="/cotizar?marca=Subaru"
          class="inline-flex items-center justify-center px-10 py-4 bg-white text-[#003087] font-bold rounded-md text-base
                 transition-all duration-200 hover:bg-slate-100 shadow-lg active:scale-[0.98]"
        >
          Solicitar Cotización Gratis
          <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
        </router-link>
      </div>
    </section>

  </div>
</template>
