<script setup>
defineProps({
  product: { type: Object, required: true },
})

const categoryIcons = {
  Frenos: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4',
  Motor: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
  'Suspensión': 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
  'Transmisión': 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15',
  'Eléctrico': 'M13 10V3L4 14h7v7l9-11h-7z',
  Filtros: 'M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z',
  'Carrocería': 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
  'Refrigeración': 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
}
</script>

<template>
  <div class="card group flex flex-col">
    <!-- Image area -->
    <div class="relative h-44 bg-slate-50 flex flex-col items-center justify-center border-b border-slate-200">
      <div class="w-16 h-16 bg-[#E8F2FB] rounded-2xl flex items-center justify-center group-hover:bg-[#0055A5]/10 transition-colors">
        <svg class="w-8 h-8 text-[#0055A5]" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" :d="categoryIcons[product.category] || 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'"/>
        </svg>
      </div>
      <p class="text-slate-300 text-xs font-mono mt-2">{{ product.partNumber }}</p>

      <!-- Tags top-left -->
      <div class="absolute top-3 left-3 flex flex-wrap gap-1">
        <span
          v-for="tag in product.tags.slice(0,2)"
          :key="tag"
          class="tag"
        >{{ tag }}</span>
      </div>

      <!-- Category top-right -->
      <span class="absolute top-3 right-3 text-[10px] font-medium text-slate-500 bg-white border border-slate-200 px-2 py-0.5 rounded-full">
        {{ product.category }}
      </span>
    </div>

    <!-- Content -->
    <div class="flex flex-col flex-1 p-5">
      <h3 class="text-slate-900 font-semibold leading-snug group-hover:text-[#0055A5] transition-colors line-clamp-2 mb-2">
        {{ product.name }}
      </h3>

      <p class="text-slate-500 text-sm leading-relaxed mb-4 line-clamp-2 flex-1">
        {{ product.description }}
      </p>

      <!-- Compatible brands -->
      <div class="flex flex-wrap gap-1.5 mb-4">
        <span
          v-for="brand in product.brands"
          :key="brand"
          class="inline-block px-2 py-0.5 text-xs bg-slate-50 text-slate-500 rounded border border-slate-200"
        >{{ brand }}</span>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between pt-4 border-t border-slate-100">
        <span class="text-slate-400 text-xs">Años: {{ product.years }}</span>
        <div class="flex items-center gap-2">
          <router-link :to="`/producto/${product.id}`" class="btn-ghost text-xs px-3 py-1.5">Ver más</router-link>
          <router-link
            :to="`/cotizar?marca=${product.brands[0]}&producto=${encodeURIComponent(product.name)}`"
            class="btn-primary text-xs px-3 py-1.5"
          >Cotizar</router-link>
        </div>
      </div>
    </div>
  </div>
</template>
