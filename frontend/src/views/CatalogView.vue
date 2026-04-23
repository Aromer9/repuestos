<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ProductFilter from '../components/catalog/ProductFilter.vue'
import ProductGrid from '../components/catalog/ProductGrid.vue'
import { useProducts } from '../composables/useProducts.js'

const route = useRoute()
const { searchQuery, selectedBrand, selectedCategory, filteredProducts, brands, categories, resetFilters } = useProducts()

onMounted(() => {
  if (route.query.marca) selectedBrand.value = route.query.marca
  if (route.query.categoria) selectedCategory.value = route.query.categoria
})
</script>

<template>
  <div class="pt-[72px] min-h-screen bg-white">
    <!-- Page header -->
    <div class="bg-slate-50 border-b border-slate-200 py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <p class="text-[#0055A5] text-[11px] font-semibold uppercase tracking-widest mb-1.5">Catálogo</p>
            <h1 class="text-3xl md:text-4xl font-bold text-slate-900">Repuestos disponibles</h1>
            <p class="text-slate-500 mt-2">Encuentra el repuesto exacto para tu vehículo japonés.</p>
          </div>
          <router-link to="/cotizar" class="btn-primary text-sm px-5 py-2.5 self-start sm:self-auto whitespace-nowrap">
            ¿No encuentras tu repuesto?
          </router-link>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <!-- Filters -->
      <div class="mb-6">
        <ProductFilter
          v-model:searchQuery="searchQuery"
          v-model:selectedBrand="selectedBrand"
          v-model:selectedCategory="selectedCategory"
          :brands="brands"
          :categories="categories"
          :totalResults="filteredProducts.length"
          @reset="resetFilters"
        />
      </div>

      <!-- Active filter pills -->
      <div v-if="selectedBrand || selectedCategory" class="flex flex-wrap gap-2 mb-6">
        <span
          v-if="selectedBrand"
          class="inline-flex items-center gap-1.5 px-3 py-1 bg-[#E8F2FB] text-[#0055A5] text-xs font-semibold rounded-full border border-[#0055A5]/20"
        >
          Marca: {{ selectedBrand }}
          <button @click="selectedBrand = ''" class="hover:text-[#003087] transition-colors">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </span>
        <span
          v-if="selectedCategory"
          class="inline-flex items-center gap-1.5 px-3 py-1 bg-[#E8F2FB] text-[#0055A5] text-xs font-semibold rounded-full border border-[#0055A5]/20"
        >
          Categoría: {{ selectedCategory }}
          <button @click="selectedCategory = ''" class="hover:text-[#003087] transition-colors">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </span>
      </div>

      <ProductGrid :products="filteredProducts" />
    </div>
  </div>
</template>
