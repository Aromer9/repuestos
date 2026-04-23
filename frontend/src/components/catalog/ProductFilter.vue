<script setup>
defineProps({
  searchQuery: String,
  selectedBrand: String,
  selectedCategory: String,
  brands: Array,
  categories: Array,
  totalResults: Number,
})

const emit = defineEmits(['update:searchQuery', 'update:selectedBrand', 'update:selectedCategory', 'reset'])
</script>

<template>
  <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
    <!-- Search -->
    <div class="relative mb-4">
      <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
      <input
        type="text"
        placeholder="Buscar por nombre, marca, modelo..."
        class="input-field pl-10 text-sm"
        :value="searchQuery"
        @input="emit('update:searchQuery', $event.target.value)"
      />
    </div>

    <!-- Selects -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
      <div>
        <label class="label text-xs">Marca</label>
        <select
          class="input-field text-sm"
          :value="selectedBrand"
          @change="emit('update:selectedBrand', $event.target.value)"
        >
          <option value="">Todas las marcas</option>
          <option v-for="brand in brands" :key="brand" :value="brand">{{ brand }}</option>
        </select>
      </div>
      <div>
        <label class="label text-xs">Categoría</label>
        <select
          class="input-field text-sm"
          :value="selectedCategory"
          @change="emit('update:selectedCategory', $event.target.value)"
        >
          <option value="">Todas las categorías</option>
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>
    </div>

    <!-- Results + reset -->
    <div class="flex items-center justify-between">
      <span class="text-slate-400 text-xs">{{ totalResults }} resultado{{ totalResults !== 1 ? 's' : '' }}</span>
      <button
        v-if="searchQuery || selectedBrand || selectedCategory"
        class="text-[#0055A5] text-xs hover:text-[#003087] transition-colors flex items-center gap-1 font-medium"
        @click="emit('reset')"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
        </svg>
        Limpiar filtros
      </button>
    </div>
  </div>
</template>
