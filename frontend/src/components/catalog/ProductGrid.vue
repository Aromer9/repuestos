<script setup>
import ProductCard from './ProductCard.vue'
defineProps({ products: { type: Array, required: true } })
</script>

<template>
  <div>
    <!-- Empty state -->
    <div v-if="products.length === 0" class="text-center py-20">
      <div class="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>
      <h3 class="text-slate-600 font-medium mb-2">No se encontraron repuestos</h3>
      <p class="text-slate-400 text-sm">Intenta con otros filtros o términos de búsqueda.</p>
    </div>

    <!-- Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      <ProductCard v-for="product in products" :key="product.id" :product="product" />
    </div>
  </div>
</template>
