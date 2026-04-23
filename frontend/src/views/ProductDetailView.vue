<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProducts } from '../composables/useProducts.js'

const route = useRoute()
const router = useRouter()
const { getProductById, allProducts } = useProducts()

const product = computed(() => getProductById(route.params.id))
const relatedProducts = computed(() => {
  if (!product.value) return []
  return allProducts.filter(p => p.id !== product.value.id && p.category === product.value.category).slice(0, 4)
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
  <div class="pt-[72px] min-h-screen bg-white">

    <!-- Not found -->
    <div v-if="!product" class="flex flex-col items-center justify-center py-40 text-center px-4">
      <div class="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      </div>
      <h2 class="text-slate-900 font-semibold text-xl mb-2">Producto no encontrado</h2>
      <p class="text-slate-500 text-sm mb-6">El repuesto que buscas no existe en nuestro catálogo.</p>
      <router-link to="/catalogo" class="btn-primary">Ver catálogo</router-link>
    </div>

    <template v-else>
      <!-- Breadcrumb -->
      <div class="bg-slate-50 border-b border-slate-200 py-3.5">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav class="flex items-center gap-2 text-sm">
            <router-link to="/" class="text-slate-400 hover:text-[#0055A5] transition-colors">Inicio</router-link>
            <span class="text-slate-300">/</span>
            <router-link to="/catalogo" class="text-slate-400 hover:text-[#0055A5] transition-colors">Catálogo</router-link>
            <span class="text-slate-300">/</span>
            <span class="text-slate-600 truncate max-w-xs">{{ product.name }}</span>
          </nav>
        </div>
      </div>

      <!-- Main content -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">

          <!-- Image placeholder -->
          <div class="bg-slate-50 border border-slate-200 rounded-2xl h-80 lg:min-h-72 flex flex-col items-center justify-center gap-4">
            <div class="w-24 h-24 bg-[#E8F2FB] rounded-3xl flex items-center justify-center">
              <svg class="w-12 h-12 text-[#0055A5]" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" :d="categoryIcons[product.category] || 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'"/>
              </svg>
            </div>
            <p class="text-slate-400 text-xs font-mono">{{ product.partNumber }}</p>
            <div class="flex flex-wrap gap-2 justify-center px-6">
              <span v-for="tag in product.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>

          <!-- Info -->
          <div class="flex flex-col">
            <div class="flex items-center gap-2 mb-3">
              <span class="tag">{{ product.category }}</span>
              <span class="text-slate-400 text-xs font-mono">{{ product.partNumber }}</span>
            </div>

            <h1 class="text-3xl md:text-4xl font-bold text-slate-900 mb-4 leading-tight">{{ product.name }}</h1>
            <p class="text-slate-500 text-base leading-relaxed mb-8">{{ product.description }}</p>

            <!-- Details -->
            <dl class="grid grid-cols-2 gap-x-6 gap-y-5 mb-8 py-6 border-y border-slate-200">
              <div>
                <dt class="text-slate-400 text-xs uppercase tracking-wider mb-1.5">Marcas compatibles</dt>
                <dd class="flex flex-wrap gap-1.5">
                  <span v-for="brand in product.brands" :key="brand"
                    class="px-2.5 py-0.5 bg-slate-50 text-slate-600 text-xs rounded border border-slate-200">
                    {{ brand }}
                  </span>
                </dd>
              </div>
              <div>
                <dt class="text-slate-400 text-xs uppercase tracking-wider mb-1.5">Años</dt>
                <dd class="text-slate-900 font-semibold">{{ product.years }}</dd>
              </div>
              <div class="col-span-2">
                <dt class="text-slate-400 text-xs uppercase tracking-wider mb-1.5">Modelos compatibles</dt>
                <dd class="text-slate-600 text-sm">{{ product.models.join(', ') }}</dd>
              </div>
            </dl>

            <!-- Notice -->
            <div class="bg-[#E8F2FB] border border-[#0055A5]/15 rounded-xl p-4 mb-8">
              <p class="text-slate-600 text-sm leading-relaxed">
                <span class="text-[#003087] font-semibold">Sin precio visible.</span>
                Cotizamos directamente con proveedores para ofrecerte el mejor precio del mercado.
                Solicita tu cotización gratuita y te respondemos en menos de 24 horas.
              </p>
            </div>

            <!-- Actions -->
            <div class="flex flex-col sm:flex-row gap-3">
              <router-link
                :to="`/cotizar?marca=${product.brands[0]}&producto=${encodeURIComponent(product.name)}&modelo=${product.models[0]}`"
                class="btn-primary flex-1 justify-center py-4"
              >
                Solicitar Cotización
                <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
                </svg>
              </router-link>
              <button @click="router.back()" class="btn-secondary px-6 py-4">← Volver</button>
            </div>
          </div>
        </div>

        <!-- Related -->
        <div v-if="relatedProducts.length">
          <h2 class="text-xl font-bold text-slate-900 mb-6">Otros repuestos en <span class="text-[#0055A5]">{{ product.category }}</span></h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <router-link
              v-for="rel in relatedProducts"
              :key="rel.id"
              :to="`/producto/${rel.id}`"
              class="card p-5 group"
            >
              <div class="w-10 h-10 bg-[#E8F2FB] rounded-xl flex items-center justify-center mb-3 group-hover:bg-[#0055A5]/10 transition-colors">
                <svg class="w-5 h-5 text-[#0055A5]" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" :d="categoryIcons[rel.category] || 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'"/>
                </svg>
              </div>
              <h3 class="text-slate-700 text-sm font-semibold group-hover:text-[#0055A5] transition-colors leading-snug mb-1">{{ rel.name }}</h3>
              <p class="text-slate-400 text-xs">{{ rel.brands.join(', ') }}</p>
            </router-link>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
